# VESC DBC
CAN Message decoding for ESCs with firmware from Benjamin Vedder: https://github.com/vedderb/bldc / https://vesc-project.com/

Work in Progress, be careful when useing it....

If there is any feedback, feel free to ping me in one of the forum treads:
- https://forum.esk8.news/t/vesc-can-dbc-development/43358
- https://vesc-project.com/node/2678
or create an issue.

 ## Credit / Resources:
- https://github.com/vedderb/bldc
- https://vesc-project.com
- https://vesc-project.com/node/649
- https://electric-skateboard.builders/t/vesc-can-message-structure/98092
- https://vesc-project.com/node/892
- https://vesc-project.com/node/1450
- https://triforce-docs.readthedocs.io/en/latest/canbus/canbus.html#canbus-control

## Missing Messages:
-	CAN_PACKET_FILL_RX_BUFFER               :5
-	CAN_PACKET_FILL_RX_BUFFER_LONG          :6
-	CAN_PACKET_PROCESS_RX_BUFFER            :7
-	CAN_PACKET_PROCESS_SHORT_BUFFER         :8
- 	CAN_PACKET_PING                         :18
-	CAN_PACKET_PONG                         :19
-	CAN_PACKET_DETECT_APPLY_ALL_FOC         :20
-	CAN_PACKET_DETECT_APPLY_ALL_FOC_RES     :21
-	CAN_PACKET_CONF_CURRENT_LIMITS          :22
-	CAN_PACKET_CONF_STORE_CURRENT_LIMITS    :23
-	CAN_PACKET_CONF_CURRENT_LIMITS_IN       :24
-	CAN_PACKET_CONF_STORE_CURRENT_LIMITS_IN :25
-	CAN_PACKET_CONF_FOC_ERPMS               :26
-	CAN_PACKET_CONF_STORE_FOC_ERPMS         :27
-	CAN_PACKET_POLL_TS5700N8501_STATUS      :29
-	CAN_PACKET_CONF_BATTERY_CUT             :30
-	CAN_PACKET_CONF_STORE_BATTERY_CUT       :31  
-	CAN_PACKET_SHUTDOWN                     :32