---
name: The Architecture
---

# The Architecture

The **ExtensiveTesting** solution is based on client/server architecture. Tests repository, SUT adapters are centralized in a test server to provide rapidly the same environment to all users.

The construction of the solution is assembled with severals components:

- Test server: the core of the solution with a scheduler, a test framework, tests repository, sut adapters, etc...
- Rich client: a user friendly client to write, execute and analysing tests
- Agents: active component, extend the possibility of testing
- Probes: passive component, used to collect logs, network dumps, etc...

![](/docs/images/archi-extensivetesting-2015.png)
