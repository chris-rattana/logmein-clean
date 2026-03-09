# Network Topology

## Target Design
- 1 headquarters
- multiple branches
- centralized logging backend
- centralized PostgreSQL database
- monitoring with Zabbix
- secure inter-site communication with VPN tunnels

## Main Zones
- user VLANs
- server VLAN
- admin VLAN
- monitoring VLAN

## Objectives
- segment traffic
- protect database access
- ensure availability
- allow centralized supervision
