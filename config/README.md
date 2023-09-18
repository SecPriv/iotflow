# IoTFlow Config

Configuration files for [data flow analysis](dfa/) and [value set analysis](vsa/)


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

* Value Set Analysis
    * [AMQP](vsa/amqp.json)
    * [COAP](vsa/coap.json)
    * [Crypto](vsa/javaCrypto.json)
    * [HTTP](vsa/endpoints.json)
    * [MQTT](vsa/mqtt.json)
        * [Webview](vsa/webview.json)
    * [UDP](vsa/udp.json)
    * [XMPP](vsa/xmpp.json)
* Flow Analysis
    * Pointer Analysis
        * [Connection only relevant for sources](dfa/connection_run_source/)
        * [Connections relevant for sources and sink](dfa/connection_run_source_and_sink/)
        * [Connection relevant for sinks](dfa/connection_run_sink/)
    * [Bluetooth source to ICC-sink or other-sink](dfa/bl_config.xml)
    * [Local network source to ICC-sink or other-sink](dfa/local.xml)
    * [General Android API source to ICC-sink or other-sink](dfa/general.xml)
    * [ICC-source to other-sink, the actual source information is added after a flow is found](dfa/template.xml)

