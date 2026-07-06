Reconfigurable Switch: A Pure XDP Approach, Design

and Implementation

Abstract

New technologies bring benefits to life and work as well as security threats and risks.

Despite  the  increasing  investment  in  Cyber  security,  security  incidents  occurred

continuously. Lack of effective lateral movement identifying and controlling is a major

cause. In this paper, by leveraging a pure XDP approach, we present the design of the

reconfigurable switch which provides the abilities to program and orchestrate functional

modules to implement not only functions like traditional switches but also access control

from  layer  2  through  layer  7.  We  then  demonstrate  how  to  implement  the  design  by

building a prototype. We also provide a performance evaluation of the prototype showing

that  reconfigurable  switch  can  be  used  as  an  infrastructure  device  with  access  control

ability as well as an acceptable performance.

Introduction

With  new  technologies  emerging,  such  as  AI,  Big  Data,  IoT,  and  so  on,  our

businesses  are  more  efficient,  and  our  life  becomes  more  convenient.  However,  the

concerns on cyber security come together with the benefits. The attacks on cyber security,

such as APT or ransomware can damage data, privacy and secrets, assets, finances, and

even more people’s lives. Therefore, more and more cyber security devices or techniques

are implemented in our production environments. Even the AI are introducted into cyber

security domain to help people analyze the data and logs to identify the potential attacks

or security breaches.

Major  measures  for  cyber  security  work  on  board  protection,  which  prevents

attackers  from  outside.  While  others  work  on  endpoint  protection,  which  ensures  the

endpoint which connects to the network is secured. However, they are challenged. With

more and more devices connected into the environment, the board is not as clear as old-

time. Controlling a single entrance helps with very little on security. Endpoint protection

is also restricted because it relies on agent working on the protected endpoints. However,

1

批注 [KC1]: Here, should we evaluate the performance or

should we demonstrate our abilities to stop lateral

movement inside local network?

those agents may not be able to be installed onto IoT devices as well as BYOD. Therefore,

new protection philosophies are raised up, e.g. Zero-Trust, which aims to eliminate the

disadvantages of traditional cyber security. Zero-Trust brings a no-board theory, so the

protection  does  not  rely  on  the  board  check  but  requires  verification  of  each  request

everywhere at any time. It does help esp. on roaming working scenarios. However, for

most  industrial  environments  and  IoT  environments,  zero-trust  is  too  complex  to

implement. For those organizations who have implemented Zero-Trust, only less than 30%

have network microsegment enabled.

Despite so many cyber security investments, security incidents still occur on vary

environments. Lateral movement is one of the main causes of those attacks. With so many

devices (protected or unprotected) connected in the network, attackers can always find a

way to break in, e.g. phishing, sending malicious software by emails, IM tools, or portable

storage,  or  even  connecting  a  malicious  device  into  the  network. Although  the  initial

broken point is usually worthless, it can be used as an intermediate to attack other valuable

assets.  Malicious  actors

leverage

the

lateral  movement  approach

to  perform

reconnaissance tasks to locate high-value devices or data, to widespread automation tools

or  bots  to  other  vulnerable  devices,  and  ultimately  to  perform  the  attack  as  desired.

Research  showed  that  over  70%  of  successful  attacks  leveraged  lateral  movement

批注 [KC2]: https://www.elisity.com/blog/the-top-11-

techniques.  By  examining  the  whole  life  cycle  of  an  attack  incident,  it  appears  that

malicious actors spend about 80% of the time doing lateral movement tasks. Barracuda

reports that about 44% of ransomware attacks were identified during lateral movement.

Therefore, it is essential for organizations to identify and prevent lateral movements to

cyberattacks-using-lateral-movement-a-2023-2024-analysis-

for-enterprise-security-

leaders#:~:text=Lateral%20movement%20%20poses%20a,op

erational%20disruption%2C%20and%20compliance%20fines

批注 [KC3R2]: This article will be referred further for listing

protect the environment from attacking. To do so, EDR/XDR relies on endpoint agents

lateral movement attacks.

installed; internal firewalls need to segment network into different zones. Even with zero-

trust,  the  situation  is  the  same.  It  seems  that  we  lack  measure  to  identify  and  prevent

lateral movement over the network. This is because we are still focusing on the boards

and endpoints and require them to be the execute point of any security policies.

Switches  which  connect  the  whole  network  can  be  the  great  place  as  the  policy

executing point if the security mechanism of firewalls, EDR/XDR, and/or other security

devices  can  be  added  up.  It  is  necessary  to  have  a  switch  which  can  not only  process

packet forwarding effectively and efficiently as usual but also perform security checks

against the packets and execute access control policies. Programmable switches look like

a doable approach while traditional programmable switches are not for common usage

2

due to cost and complexity. In this article, we introduce the reconfigurable switch, which

is  completely  designed  based  on  XDP  (eXpress  Data  Path),  an  eBPF-based  high-

performance  network  data  path  to  transfer  network  packets  at  high  rates.  The

reconfigurable switch can work as usual switch, such as, to forward packets at layer 2 and

layer 3. Besides that, it also provides the following abilities. First, it can implement packet

examination  and  policy  execution  at  layer  2  through  layer  7  by  attaching  necessary

function modules. Second, it provides the interfaces that administrators can leverage to

develop  their  own  function  modules.  Third,  administrators  can  also  orchestrater  the

attached  function  modules  according  to  their  own  requirement  to  achieve  high-speed

packet processing and security goals as desired.

The rest sections are organized as follows. In Section 2, we provide an overview of

XDP and related concepts. Section 3 presents the whole picture of the designation of the

reconfigurable  switch.  We  then  demonstrate  how  the  reconfigurable  switch  works  by

implementing  a  prototype  in  Section  4,  following  by  a  performance  evaluation  of  the

prototype in Section 5. Finally, Section 6 outlines the future research and summarizes the

key findings in the current work.

Background

XDP

XDP  (eXpress  Data  Path)  is  a  high  performance  and  programmable  data  path

technology,  which  operates  at  the  early  stage  of  the  network  driver,  so  it  can  process

network  packets  before  they  reach  the  Linux  kernel  stack.  This  significantly  reduces

processing overhead and latency. XDP is built on eBPF (Extended Berkeley Packet Filter),

which  is  a  sandboxed  virtual  machine  in  the  Linux  kernel.  This  environment  enables

programmers to filter, redirect, modify and process packets directly in an efficient and

secure  manner.  Therefore,  XDP  is  widely  used  in  DDoS  mitigation,  network  load

balancing, traffic monitoring, and edge computing.

The XDP system consists of four main components, which are the XDP driver hook,

the  eBPF  virtual  machine,  BPF  maps,  and  eBPF  verifier. The  XDP  driver  hook  is  the

entrance  of  the  XDP  program,  which  is  executed  packets  arrive  at  the  XDP-attached

network interface card. Written in C language usually, XDP programs are compiled into

BPF byte codes and executed inside the eBPF virtual machine. The XDP programs are

3

triggered to execute when a packet arrives. Because they always start with the initial state,

the XDP programs use BPF maps to store and retrieve data in program context. BPF maps

can be used as global configuration storage, and the information share between user space

programs and kernel eBPF programs. Types of maps commonly used in XDP are Hash

Maps, Array Maps, and Ring Buffers. The former two maps are similar and useful for

maintaining  and  sharing  program  context;  while  the  latter  one,  Ring  Buffers,  enables

high-speed communication between XDP and user space programs. Since XDP operates

directly in the kernel’s memory space, any inappropriate operation could lead to kernel

panic. The eBPF verifier prevents such risks by enforcing a strict static analysis on XDP

programs before they are loaded into the kernel. If any potentially unsafe operation, e.g.

memory  out-of-bound  access,  infinite  loops,  unauthorized  function  calls,  or  unsafe

pointer dereferences, is detected, the eBPF verifier will stop loading the XDP program.

In the early days, an eBPF program is limited to no more than 4096 instructions. Tail

calls were introduced to link several programs to overcome the limitations. Although the

limitation has been enlarged to a million instructions, tail calls are still helpful to break

down complex logic into smaller, composable eBPF programs. For instance, a set of tail

calls can be used in XDP as a pipeline process to achieve packet parsing, access control,

and other operations.

XDP  programs  stop  execution  after  returning  predefined  actions.  These  actions

indicate how a packet should be processed as the table shows below.

Return Code

Action

XDP_ABORTED

Terminates execution due to an error

XDP_DROP

Drops the packet (e.g., DDoS filtering)

XDP_PASS

XDP_TX

Allows packet to enter kernel stack

Sends packet back through the same interface

XDP_REDIRECT

Redirects packet to another NIC or AF_XDP

Table 1. Predefined actions for XDP programs.

Programmable Switch

// todo:

// explain programmable switch vs cyber security, how it can help

// and why it is not a usual solution

4

Lateral Movement

// todo:

// explain how lateral movement affects cyber security.

Design

Implementation

Evaluation

Future Research and Conclusion

5

