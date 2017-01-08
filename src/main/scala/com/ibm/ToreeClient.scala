package com.ibm

import com.typesafe.config.ConfigFactory
import org.apache.toree.kernel.protocol.v5.client.boot.ClientBootstrap
import com.typesafe.config.Config
import org.apache.toree.kernel.protocol.v5.MIMEType
import org.apache.toree.kernel.protocol.v5.client.SparkKernelClient
import org.apache.toree.kernel.protocol.v5.client.boot.layers.{StandardHandlerInitialization, StandardSystemInitialization}
import org.apache.toree.kernel.protocol.v5.client.execution.DeferredExecution
import org.apache.toree.kernel.protocol.v5.content.ExecuteResult
import py4j.GatewayServer

import scala.concurrent.{Await, Promise}
import scala.concurrent.duration.Duration

class ToreeGateway(client: SparkKernelClient) {
  //  Define our callback
  def printResult(result: ExecuteResult) = {
    println(s"Result was: ${result.data.get(MIMEType.PlainText).get}")
  }

  def eval(code: String): Object = {
    val promise = Promise[String]
    val exRes: DeferredExecution = client.execute(code).onResult(er => {
      promise.success(er.data.get(MIMEType.PlainText).get)
    })

    Await.result(promise.future, Duration.Inf)
  }
}

object ToreeClient extends App {

  val profileJSON: String = """
{
    "stdin_port":   48691,
    "control_port": 44808,
    "hb_port":      49691,
    "shell_port":   40544,
    "iopub_port":   43462,
    "ip": "127.0.0.1",
    "transport": "tcp",
    "signature_scheme": "hmac-sha256",
    "key": ""
}
""".stripMargin

  // Parse our configuration and create a client connecting to our kernel
  val config: Config = ConfigFactory.parseString(profileJSON)

  val client = (new ClientBootstrap(config)
    with StandardSystemInitialization
    with StandardHandlerInitialization).createClient()

  val toreeGateway = new ToreeGateway(client)
  print(toreeGateway.eval("sc"))

  val gatewayServer: GatewayServer = new GatewayServer(toreeGateway)
  gatewayServer.start()
}
