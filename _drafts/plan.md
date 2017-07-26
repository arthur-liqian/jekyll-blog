# Overview

This is my own plan about the items to investigation. It would never be 
finallized or published out. Instead of putting action items into the a task
scheduling and tracking application, more background information of those
items and their relationships could reveal more details. That would be helpful
to improve the task output and inspire more ideas.

Usually, a task here would produce several articles, or mindmap diagrams. Sample
applications would be setup as the comphrehensive demostration of several 
related investigation tasks. They would be a separated project in git. 

# Architecture Design

This subject contains the items to improve the skill to design an enterprise
application system. The items usually covers one or more of the following 
topics:

- Application layering
- Service design
- Module design 
- Interoperation approaches between service or module level
- Business Domain Modeling
- Performance improvement from application design and implementation perspective
- High availability from application design and implementation perspective

The following topics will be covered in other subjects, although they are highly
related with architecture design:

- Class or inter-class design

    This topic will be covered in object-oriented design. This part is usually
    about the micro-design within a module or service. The design pattern of GoF
    is a typical topic.

- Infrastructure design

    Infrastruture design covers the software, tools, operation systems,
    network, storage, hardware, etc. The applications run over them, but
    infrastructure design usually doesn't consider the business details,
    although some business characters may impact the infrastucture design.

    Some important application components or tools would be also covered in this
    topic, such as database, message queue.

## Ongoing Tasks

### Patterns of Enterprise Architecture

Read [Patterns of Enterprise Architecture](https://www.amazon.com/Patterns-Enterprise-Application-Architecture-Martin/dp/0321127420)

#### Expected Output

- The mind map of the patterns and their characters
- The understanding about the pattern application, and the comparison betwween
    then similiar patterns.

#### Priority

__**Medium**__

The architecture pattern descision is import, but not always a blocker for a 
project. And this book couldn't be understood thoroughly in one shot. In this 
task, get the major characteristics of the patterns, the map of their
relationships, and their typical scenarios. Go back to this book whenever 
the detail information is required to make the choice in the future.

#### Status

- Finished reading the first part *The Narratives*, but no documents or diagram
    have been assembled. 

#### Related Task

- __**Undone**__ [Hexagonal Architecture pattern](http://alistair.cockburn.us/Hexagonal+architecture)

### Building Microservices

Read [Building Microservices](http://shop.oreilly.com/product/0636920033158.do)

#### Priority

__**Medium**__

The microservice is popular these days. Although the core thoughts of this 
approach is simple, it is still necessary to get the comphrehensive
understanding to solve some complicated issues.

#### Status

- Started reading the book and moved to *Domain Driven Design*

#### Related Task

- __**Ongoing**__ Domain-Driven Design

### Domain-Driven Design

Read [Domain-Driven Design: Tackling Complexity in the Heart of Software](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)

#### Priority

__**High**__

Business logic and modeling is the core practice in application design and 
implementation, and it is always the bottle neck to improve application. 
However, this book, at least the Chinese version, is not clear enough. More
related material should be referred to in the future. 

#### Status

- Ongoing

#### Related Task

None

# Infrastructure Design

Infrastructure design covers the following topics:

- System hardware
- Network Infrastructure
- Openration System
- Storage System
- Database
- Message Queue System
- Other service provider, like LDAP, SMTP Server, etc.
- CI/CD
- System Operation/DevOps

The competitive products or tools choosing, technical requirements, perforamnce
tunning and high availability would be included in this chapter. The business
logic related part would not be covered in detail, such as database schema 
design.

Some items could be too complex to covered within the single subject, such as
database, message queue. They would be moved to a separated suject.

## Ongoing Task

### RabbitMQ

- Read [Mastering RabbitMQ](https://www.packtpub.com/application-development/mastering-rabbitmq)
- Go through [RabbitMQ Official Document](http://www.rabbitmq.com/documentation.html)

#### Priority

__**High**__

Message queue is an important intermedia for systems, services to interact, and
impacts deeply the system design. It is also always the performance and 
availability bottle neck of the system emmploying it.

#### Status

- __**Done**__. Finished reading the book *Mastering RabbitMQ*. However, this 
    book doesn't reveal enough information about internal relationships, status,
    and implementation mechanism. More materials are required.
- __**Ongoing**__ Go through RabbitMQ official documents. 
- __**Pending**__ Setup a RabbitMQ cluster following the instructions in the 
    book. The performance and stability should be evaluated.

#### Related Task

- System administration and cluster management tools, such as Puppet, Ansible,
    Chef, Salt.
- System [Federation](https://en.wikipedia.org/wiki/Federation_(information_technology))
    such as [Federated Datdabase](https://en.wikipedia.org/wiki/Federated_database_system)
- Monitor tools, like Nagios, Munin, Zabbix
- Authentication and security service framework SASL
- SSL, OpenSSL 
- The relationship between exchange, channel, and queue is not clearly 
    described. It is necessary to go through other books and materials to 
    get the comprehensive understanding. Demo application is also required.
- The data replication and failover mechanism are not described clearly. More
    materials are needed.
- Other messaging protocol, such as [STOMP](https://stomp.github.io/), 
    [MQTT](http://mqtt.org/)
- SELinux

# Technical Solutions

## Planning Task

### GPGPU

#### Priority

__**Media**__

#### Status

- __**Pending**__ OpenCL

#### Related Task

- GPGPU Database 

# Personal Project

## Mind Map plugin for VSCode

Rerferring to yUML plugin