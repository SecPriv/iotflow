# IoTFlow configuration

Configuration files used by the Docker setup:
- **Value set analysis (VSA):** [`VSA/docker/config/`](../../../VSA/docker/config/). The flow stage runs the same analyses from its own copy, [`iotscope/`](iotscope/) (identical files, plus `source.json` / `sink.json`).
- **Flow analysis (FlowDroid):** this folder.

The exclusion lists (`exclude.json`, `exclude_large.json`) are described in [CHANGES.md](../../../CHANGES.md) ("Exclusion lists").


## Sources and Sinks


A list of base package names from network, cryptographic, Bluetooth, and ICC related methods we use as sources or sinks.

* AMQP
    * com.azure.core.amqp
    * com.rabbitmq
* Bluetooth
    * android.bluetooth.BluetoothAdapter.LeScanCallback
    * android.bluetooth.BluetoothGatt
    * android.bluetooth.BluetoothGattCallback
    * android.bluetooth.BluetoothGattService
    * android.bluetooth.BluetoothSocket
* CoAP
    * com.google.iot
    * org.eclipse.californium
    * org.ws4d.coap.core
* Crypto
    * javax.crypto
    * javax.security
* ICC
    * android.content.SharedPreferences
    * android.content.Intent
    * android.os.Bundle
* MQTT
    * com.amazonaws.mobileconnectors.iot
    * com.hivemq
    * com.tuya.smart
    * io.x2ge.mqtt
    * org.eclipse.paho
    * org.fusesource.mqtt
* HTTP
    * android.webkit.WebView
    * com.android.volley
    * com.bumptech.glide
    * com.loopj.android.http
    * java.net.DatagramPacket
    * java.net.DatagramSocket
    * java.net.Socket
    * java.net.URL
    * okhttp3
    * org.apache.http
    * retrofit2
* XMPP
    * org.jivesoftware.smack
    * org.jxmpp
* Other from FlowDroid
    * android.accounts.AccountManager
    * android.bluetooth.BluetoothAdapter
    * android.content.pm.PackageManager
    * android.location
    * android.media.AudioRecord
    * android.net.wifi
    * android.provider.Browser
    * android.telephony
    * android.telephony.TelephonyManager
    * android.telephony.gsm
    * java.io
    * java.util.Calendar
    * java.util.Locale
    * javax.servlet.http
    * org.apache.xmlrpc
    * org.springframework.web.servlet


For more details, see the respective files:

* Value Set Analysis (`VSA/docker/config/`)
    * [AMQP](../../../VSA/docker/config/amqp.json)
    * [CoAP](../../../VSA/docker/config/coap.json)
    * [Crypto](../../../VSA/docker/config/javaCrypto.json)
    * [HTTP](../../../VSA/docker/config/endpoints.json)
    * [MQTT](../../../VSA/docker/config/mqtt.json)
    * [WebView](../../../VSA/docker/config/webview.json)
    * [UDP](../../../VSA/docker/config/udp.json)
    * [XMPP](../../../VSA/docker/config/xmpp.json)
    * [Taint rules](../../../VSA/docker/config/taintrules.json)
    * [Requests](iotscope/requests.json)
* Flow Analysis (this folder)
    * Pointer analysis
        * [Connections relevant for sources](source_connection/)
        * [Connections relevant for sources and sinks](both/)
        * [Connections relevant for sinks](sink_connection/)
    * [Bluetooth source to ICC sink or other sink](bl_config.xml)
    * [Local network source to ICC sink or other sink](local.xml)
    * [General Android API source to ICC sink or other sink](general.xml)
    * [ICC source to other sink; the actual source information is added after a flow is found](template.xml)
    * Taint wrapper summaries: [summariesManual/](summariesManual/), [easy_tain_wrapper.txt](easy_tain_wrapper.txt)
