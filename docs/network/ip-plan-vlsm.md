# IP Plan (VLSM)

## Example Logic
Use VLSM to allocate subnet sizes according to site size and function.

Example approach:
- /24 for headquarters users
- /26 for branch users
- /27 for servers
- /28 for administration
- /28 for monitoring

## Goal
- optimize address usage
- keep room for growth
- simplify routing and ACL design
