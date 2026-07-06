Kyle Cui

发件人:
发送时间:

收件人:
抄送:
主题:

Dear Norman,

Yin Cui
2009年1月30日星期五 14:22
'Norman.Choo@shell.com'; Norjehan.Mehdzar@shell.com; Edna.Rajah@shell.com
KL Based TAM's working on Shell; Fei-Yau.Lim@shell.com; Kong-Tat.Shia@shell.com
RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to QSR-
S-01001

Thanks for the reply. I am glad to hear that the cause on the network has been found and the issue is resolved.

Based on your confirmation, I am going ahead to close this case. For your records, I summarized the key points
below:

Symptoms:
=========
Messages from AMSDC1-s-03326 to QSR-S-01001 were stuck in the remote delivery queue.

Cause:
======
Exchange server will send x-exps BLOB for authentication. However, only partial BLOB was received by the remote
server. Thus, the remote server kept the session waiting till it timed out. It appears that a network device dropped
some packets containing the BLOB and caused the problem.

Resolution:
=========
Your network team re-configured the device to bypass all email traffics and resolved the issue.

Once again, I would like to thank you for contacting Microsoft Enterprise Communication Support Service. I hope
that you were delighted with the service provided to you.

If you require further assistance regarding this issue, please feel free to write to me directly with any supplemental
information. The issues will then be reopened and forwarded back to me for follow-up. I am happy to be of
assistance.

Thank you for choosing Microsoft.

Yin Cui

Escalation Engineer, Enterprise Communication Support Team
Commercial Technical Support Enterprises
APGC Customer Service & Support

Mailto: kylecui@microsoft.com
Phone:86-21-61514571

Delighting our customers is our #1 priority.
We welcome your comments and suggestions about how we can improve the support we provide to you. You can also contact my manager, Jeff Chen at (86-
21)6469-1188 ext. 4349 or by sending email to: jeffchen@microsoft.com.

From: Norman.Choo@shell.com [mailto:Norman.Choo@shell.com]
Sent: Friday, January 30, 2009 1:11 PM
To: Yin Cui; Norjehan.Mehdzar@shell.com; Edna.Rajah@shell.com

1

Cc: KL Based TAM's working on Shell; Fei-Yau.Lim@shell.com; Kong-Tat.Shia@shell.com
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to QSR-S-01001

Thanks, Yin :) Just minutes after I sent this email to you, the network found the cause. It was traffic shaping by the
Riverbed devices in Amsterdam which somehow resulted in the packet drops seen on QSR-S-01001. Armed with this
information, they placed a workaround which involved a by-pass rule for all email traffic - hence no email traffic is
optimized/shaped by the Riverbed devices. Immediately we see mails flowing and the issues resolved.

Obviously, your detailed analysis and clear explanation on the findings were key to convincing the network folks
where the problem lies - i.e. outside the Exchange servers. As the cause is clear, we can have this case closed :)
Many thanks for your tireless effort this week in helping solve this rather complex problem.

Regards,
Norman Choo

-----Original Message-----
From: Yin Cui [mailto:kylecui@microsoft.com]
Sent: 30 January 2009 11:19
To: Choo, Norman SITI-ITSS-EUC; Mehdzar, Norjehan SITI-ITSS-EUC; Rajah, Edna R SITI-ITSS-EUC
Cc: KL Based TAM's working on Shell; Lim, Fei-Yau SITI-ITSS-EUC; Shia, Kong-Tat KT SITI-ITSS-EUC
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to QSR-S-01001

Hi Norman,

Thanks for sending me the netmon trace.

I picked one of the SMTP sessions (port 8642 on amsdc1-s-03326) to review and the result is same.

AMSDC1-s-03326 sent the x-exps GSSAPI BLOB as below:

While QSR-s-01001 received the tail only:

If your network team has different findings, or if you have any further questions, please feel free to let me
know.

Thanks & Regards,
Yin

From: Norman.Choo@shell.com [mailto:Norman.Choo@shell.com]
Sent: Friday, January 30, 2009 1:28 AM
To: Yin Cui; Norjehan.Mehdzar@shell.com; Edna.Rajah@shell.com
Cc: KL Based TAM's working on Shell; Fei-Yau.Lim@shell.com; Kong-Tat.Shia@shell.com
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to QSR-S-01001

Hi Yin,
We just performed another test while enabling Netmon on QSR-S-01001 & AMSDC1-S-03326 and a network
sniffer on the switch, which QSR-S-01001 is connected to. While the internal network team is looking at this,
can you also analyze the captures and comment? Thanks.

Regards,

2

Norman Choo

-----Original Message-----
From: Yin Cui [mailto:kylecui@microsoft.com]
Sent: 29 January 2009 17:48
To: Choo, Norman SITI-ITSS-EUC; Mehdzar, Norjehan SITI-ITSS-EUC; Rajah, Edna R SITI-ITSS-EUC
Cc: KL Based TAM's working on Shell; Lim, Fei-Yau SITI-ITSS-EUC; Shia, Kong-Tat KT SITI-ITSS-EUC
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to QSR-S-
01001

Welcome.

I am looking forward to hearing how it goes. Please feel free to let me know if you need any further
information.

Thanks & Regards,
Yin

From: Norman.Choo@shell.com [mailto:Norman.Choo@shell.com]
Sent: Thursday, January 29, 2009 1:46 PM
To: Yin Cui; Norjehan.Mehdzar@shell.com; Edna.Rajah@shell.com
Cc: KL Based TAM's working on Shell; Fei-Yau.Lim@shell.com; Kong-Tat.Shia@shell.com
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to QSR-S-
01001

Thanks, Yin. This clarification helps :) We'll update you when any new developments arise in our
internal investigation.

Regards,
Norman Choo

-----Original Message-----
From: Yin Cui [mailto:kylecui@microsoft.com]
Sent: 29 January 2009 12:12
To: Choo, Norman SITI-ITSS-EUC; Mehdzar, Norjehan SITI-ITSS-EUC; Rajah, Edna R SITI-
ITSS-EUC
Cc: KL Based TAM's working on Shell; Lim, Fei-Yau SITI-ITSS-EUC; Shia, Kong-Tat KT SITI-
ITSS-EUC
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to
QSR-S-01001

Hi Norman,

Thanks for the reply. The hotfix should not be related to this issue.

And the network monitor’s driver will capture all the packets with the network adapter,
thus the missing packets are not related to OS. Instead, it indicates that the NIC didn’t
receive the packet.

I hope this helps to clarify.

Thanks & Regards,
Yin

From: Norman.Choo@shell.com [mailto:Norman.Choo@shell.com]
Sent: Thursday, January 29, 2009 11:28 AM
To: Yin Cui; Norjehan.Mehdzar@shell.com; Edna.Rajah@shell.com
Cc: KL Based TAM's working on Shell; Fei-Yau.Lim@shell.com; Kong-Tat.Shia@shell.com

3

Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail only to
QSR-S-01001

Yin,
The issue is still being worked on with the network folks in Shell. Just to ensure we cover all
angles, at the time below, the server was rebooted to allow the Hotfix KB958687 to take
effect. Can you confirm whether this is not causing the data loss shown in your investigation?

Another way of asking this is, during a Netmon packet capture, are these exactly what was
sniffed off the network unaltered by the OS?

 1/23/2009  3:24:17 AM  Abnormal Shutdown    Prior uptime:35d 0h:8m:29s
 1/23/2009  3:30:37 AM  Boot                 Prior downtime:0d 0h:6m:20s

Event Type: Information
Event Source: NtServicePack
Event Category: None
Event ID: 4377
Date:  1/20/2009
Time:  8:01:20 PM
User:  NT AUTHORITY\SYSTEM
Computer: QSR-S-01001
Description:
Windows Server 2003 Hotfix KB958687 was installed.

For more information, see Help and Support Center at
http://go.microsoft.com/fwlink/events.asp.

Regards,
Norman Choo

-----Original Message-----
From: Yin Cui [mailto:kylecui@microsoft.com]
Sent: 27 January 2009 00:42
To: Choo, Norman SITI-ITSS-EUC; Mehdzar, Norjehan SITI-ITSS-EUC; Rajah, Edna
R SITI-ITSS-EUC
Cc: KL Based TAM's working on Shell
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail
only to QSR-S-01001

Thanks for your reply Norman. It has been a great pleasure in working with you and
your team.

Please feel free to let me know if there is any further question. I am glad to be of
any assistance.

Enjoy your Chinese New Year holidays!

Regards,
Yin

From: Norman.Choo@shell.com [mailto:Norman.Choo@shell.com]
Sent: Tuesday, January 27, 2009 12:34 AM
To: Yin Cui; Norjehan.Mehdzar@shell.com; Edna.Rajah@shell.com
Cc: KL Based TAM's working on Shell
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has queued mail
only to QSR-S-01001

4

Thanks, Yin This is excellent work :). We'll bring your findings to the network guys
and hopefully find where and why the packets are dropped. Meanwhile, please lower
the severity to C for this case. Have a Happy Chinese New Year :)

Regards,
Norman Choo

-----Original Message-----
From: Yin Cui [mailto:kylecui@microsoft.com]
Sent: 27 January 2009 00:28
To: Mehdzar, Norjehan SITI-ITSS-EUC; Choo, Norman SITI-ITSS-EUC;
Rajah, Edna R SITI-ITSS-EUC
Cc: KL Based TAM's working on Shell
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has
queued mail only to QSR-S-01001

Dear Norjehan & Norman,

Thanks for your time tonight in working with us on this issue.

Here are our findings so far.

1.       The connection from the BH servers to QSR-S-01001 was dropped

by QSR-S-01001 due to the error
451+Timeout+waiting+for+client+input

2.       The event logs on the BH servers also indicated for the same:

Event Type:        Warning
Event Source:    MSExchangeTransport
Event Category:                SMTP Protocol
Event ID:              7002
Date:                     1/26/2009
Time:                     1:26:12 PM
User:                     N/A
Computer:          AMSDC1-S-03326
Description:
This is an SMTP protocol warning log for virtual server ID 1,
connection #31. The remote host "156.31.220.134", responded to
the SMTP command "x-exps" with "451". The full command sent
was "X-EXPS
".  This may cause the connection to fail.

3.       According to the SMTP logs and the event logs, the 451 timeout

error occurred after the BH servers attempted to authenticate itself
to QSR-S-01001 server after the x-exps GSSAPI command.

4.       X-EXPS GSSAPI command is issued by the BH server which means
the BH server attempted to use Kerberos authentication. After the
command the BH server will send out the authentication BLOB (in
binary) to the QSR-S-01001. Normally, QSR-S-01001 will return the
result of authentication back in order to move the transmission
forward.

5.       So we captured network monitor traces on both servers.

a.       On the BH server, we can see the authentication BLOB was

sent out already

5

b.      However, on the QSR-S-01001 server, only the tail of the

BLOB was received.

As the QSR-S-01001 server didn’t receive the whole BLOB, it
kept waiting for other data until it timed out in 10 minutes.

c.       Here is the BLOB on both BH and QSR-S-01001 ends.

BH:
YIIGIwYGKwYBBQUCoIIGFzCCBhOgMDAuBgkqhkiC9xIBAgIG
CSqGSIb3EgECAgYKKoZIhvcSAQICAwYKKwYBBAGCNwICCqK
CBd0EggXZYIIF1QYJKoZIhvcSAQICAQBuggXEMIIFwKADAgEF
oQMCAQ6iBwMFACAAAACjggTdYYIE2TCCBNWgAwIBBaEVG
xNBRlJJQ0EtTUUuU0hFTEwuQ09NojUwM6ADAgECoSwwKh
sHU01UUFNWQxsfcXNyLXMtMDEwMDEuYWZyaWNhLW1lL
nNoZWxsLmNvbaOCBH4wggR6oAMCARehAwIBEqKCBGwEg
gRoJWSfS2f6PmxcuzUKPY8tDMkJOZ0KwjzEzaXq0vHXt6DGT
RB1UNRIAHwDpyrEh2eIIxBH5Gk8l7+u7rcr7IE5MmvJnNpSiJ
mmug+VLrWLb5Cly4oYqnS7Cl/hp64xI6UgCl58TIe3tqEIElJx7
XR
UcMstQfU5cXxS1DBV2y2/F8rL/k6aHMWSQgtAR1oKAIoC+c
OoyMLV3wMiITolsXZdg0Y/LV0w8DVjYSmiCkNLhMsV02T9Y
eJ
Evfmgypq3yMV2fDcarfnIRcLX0xPRkQyY1xr0/azWFtgpp0nw
54Y9xbdLOrq8tO6FLuT5hgJUFqbx8lnvUnpq8kzfp4qLgMF/m
L
qdibqXR2a0fGBhtfgb3naMXI1+po/lt/ytYwnpl/zdSaM4EPwV
xv2kr9IhRi/3XszswkTTpFvDfThupMtYOEEzF5N/kZvDAtPHXdI
IPP61VzPdJa9pEHGjs6Q/cDRUHlZss3SUrxT0rgZpNhm8OGCV
js33rzy+c3OXg3Q2UqJ6jDAUn40GnyP6Ep7J55wDazt2z36hgJ
f

6

XT9+L/dkIuBO8kGM8V7U3DWo6ZxkixaOnIXX5Ez7yA4VPqv6
2mySA55M/3iRZ1LrsZeozjAiVoqn8PRSh1KOY6/dioni/8XXDn
j
/OWQLqf+5nYLnx7dpieKx/IitfP8EqC28k4f0BPdB3qTPQaSHJ
urrY7sD5wG9s/MY3RJMzQarWMEvFiCt+lL3r/lhZsLo86mpl9
5x
OYhxpooLDxKrpvbrDAWWvf6Et9eXCiTCBP2/jnGXSuQeeDK
HjlO/vqbXKYS6pfSPd0Pl92Sv16YA+Wcsjb6me0vVHshfHYDy
13
iY4KR5rINF5m66nZNamPQiKdX9gPaJ2095ksQLGl7pud9QwL
UJNr2TKcnpJnXjLMMvNlXktPrGVQLW3DD6W3OaCBP3Ik2Oz
m
fxrneHPLJpYPusMtfxgisT2a0MOuZufLQJDMw7I3PPjtZPzpxxr
tOHYST51iBmQVHQrtTF7LdFasTz9uMGOYuoe08PktqEmkER
N
hmcsjcxJ2gRW+fV3HyoHUn5/DB6mT5VibZEGwac7JE9h+ba6
c1YVoHvCsQ4dklgvEHbMKRxXUmXdxYRSuU6PO7lSfxTug4Q
7o
Dc5xVqaZOATGzxhF7rLX7hT0IZ0zfurgBnFXD47cuK219WZX7
yuTOggX9b5v+1xTZxMeXa3dQM0jSUFRpPXjbcFMIrSYsv/C3f
L3
SUa1uAjvIvq/hfobW/FOVH567S3mW2aRQ2+wknl5NDEgsw
awGj3A7x+xCz7eTwXrCsZRj8Atk+7epkP19XILqRcysZMZgm
Me
wla3D/FiH4dXQG3/Iv7z2OtWS7Wa95DEjzhMs5+Icdfn3MG5
XBpOy8gmRhBbm9/BuCMYTj1eyh048KZ5c/LYXXxnq3Wer7X
+o
zyiP0f3113uEds6QxNYnvjU5bDwexhX96mQf3+hpnocp2V3H
7XD/UXYErxG/Ng+Z/x7c3wKUcjA8eKpIHJMIHGoAMCAReigb
4
EgbtX4n3DCz25wIPubjUOyp2c1LAVmWT6vhNslHXwfzWRH
eKTPGB3+M7rnHXPhcduZkUdxcwWMnvS/0okvrDI5BI88la0
8yEj
C4vC4GlsVYag/WEeqoinpEs7hatPmweVD5b57NnWjut4KjrA
sWy6tNi2HWqZ7MFwuruawZhqAnDngljCRRI3DXL9IiBJA7e8
qRja
KZsbxfaDSIx3Poxu/B5RXbEtos1YBdjWyU6S2WrzGBn7h9hfQ
VK0nt9D..
QSR-S-01001:
fxTug4Q7oDc5xVqaZOATGzxhF7rLX7hT0IZ0zfurgBnFXD47cu
K219WZX7yuTOggX9b5v+1xTZxMeXa3dQM0jSUFRpPXjbcF
MIrSY
sv/C3fL3SUa1uAjvIvq/hfobW/FOVH567S3mW2aRQ2+wknl5
NDEgswawGj3A7x+xCz7eTwXrCsZRj8Atk+7epkP19XILqRcysZ
MZg
mMewla3D/FiH4dXQG3/Iv7z2OtWS7Wa95DEjzhMs5+Icdfn
3MG5XBpOy8gmRhBbm9/BuCMYTj1eyh048KZ5c/LYXXxnq3
Wer7X
+ozyiP0f3113uEds6QxNYnvjU5bDwexhX96mQf3+hpnocp2V
3H7XD/UXYErxG/Ng+Z/x7c3wKUcjA8eKpIHJMIHGoAMCARei
gb4E
gbtX4n3DCz25wIPubjUOyp2c1LAVmWT6vhNslHXwfzWRHe
KTPGB3+M7rnHXPhcduZkUdxcwWMnvS/0okvrDI5BI88la08y
EjC4vC

7

4GlsVYag/WEeqoinpEs7hatPmweVD5b57NnWjut4KjrAsWy6
tNi2HWqZ7MFwuruawZhqAnDngljCRRI3DXL9IiBJA7e8qRjaK
Zsbxf
aDSIx3Poxu/B5RXbEtos1YBdjWyU6S2WrzGBn7h9hfQVK0nt
9D..

So we can see that others were lost during the
transmission. A roughly calculation indicated that we lost at
least 1436+12 =1448 packets

Till now, it is clear that the issue is on the network between the two servers.
It is probably a filter dropped some packets.

A potential workaround is to disable Integrated Windows Authentication
(Kerberos) on the target server (QSR-S-01001) as we will then have different
x-exps BLOB and would not match with the pattern of any filters.

Please feel free to let me know if you have any questions or concerns.

Thanks & Regards,
Yin

From: Yin Cui
Sent: Monday, January 26, 2009 8:15 PM
To: 'Norjehan.Mehdzar@shell.com'
Cc: Norman.Choo@shell.com
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has
queued mail only to QSR-S-01001

Hi

Can you please join into the following session?

Customer's Join Information
Session URL        : http://support.microsoft.com/ea
Session ID           : 4B59BJ
Entry code is not required.

Regards,
Yin

From: Norjehan.Mehdzar@shell.com [mailto:Norjehan.Mehdzar@shell.com]
Sent: Monday, January 26, 2009 8:09 PM
To: Yin Cui
Cc: Norman.Choo@shell.com
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that has
queued mail only to QSR-S-01001

Hi Yin Cui,

Below is the error logs that are found:

Event Type: Error
Event Source: MSExchangeTransport
Event Category: SMTP Protocol
Event ID: 7004
Date:  1/26/2009

8

Time:  1:04:34 PM
User:  N/A
Computer: AMSDC1-S-03326
Description:
This is an SMTP protocol error log for virtual server ID 1, connection #1428.
The remote host "145.26.110.48", responded to the SMTP command
"xexch50" with "500 5.5.2 Error processing XEXCH50 command  ". The full
command sent was "XEXCH50  ".  This will probably cause the connection to
fail.

For more information, click http://www.microsoft.com/contentredirect.asp.

Regards,
Norjehan

-----Original Message-----
From: Yin Cui [mailto:kylecui@microsoft.com]
Sent: 26 January 2009 19:54
To: Mehdzar, Norjehan SITI-ITSS-EUC
Cc: Choo, Norman SITI-ITSS-EUC
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that
has queued mail only to QSR-S-01001

<dropping customer service center to BCC>

Hi Norjehan,

I am adding your IM. Please check if you can get my messages in
your IM.

Regards,
Yin

From: Norjehan.Mehdzar@shell.com [Norjehan.Mehdzar@shell.com]
Sent: Monday, January 26, 2009 7:39 PM
To: APAC/GCR 24x7 Customer Service Center; Yin Cui
Cc: Norman.Choo@shell.com
Subject: RE: SRS090125600006: [XCON] 3 other BH servers that
has queued mail only to QSR-S-01001

Hi Ray,

Thanks for replying.

Yes, please raise to Sev A and contact me asap.  My contact no is
as below:+6012-3096272.

I can also be contacted via IM:
norjehanmehdzar@hotmail.com.  Please do get back to us as soon
as possible as the issue is still occuring.

Thanks.

Regards,
Norjehan

-----Original Message-----
From: APAC/GCR 24x7 Customer Service Center
[mailto:gtsccsa@microsoft.com]
Sent: 26 January 2009 19:27

9

To: Mehdzar, Norjehan SITI-ITSS-EUC; Yin Cui
Cc: Choo, Norman SITI-ITSS-EUC; APAC/GCR 24x7
Customer Service Center
Subject: RE: SRS090125600006: [XCON] 3 other BH
servers that has queued mail only to QSR-S-01001

Dear Norjehan ,

Thank  you  for  contacting  the  Microsoft  Global  Technical
Support Center.

My name is Ray and I' m a Customer Service Representative.
As it is non-business hour and engineer Yin Cui may have left
office for today. Could you advice what we should do to help?
Shall we raise to Sev.A and let our on-duty engineer to do the
troubleshooting?  Or we will inform Yin Cui and do the trouble
shooting tomorrow morning? We are looking forward for your
reply.

Should  there  be  any  additional  enquires,  please  do  not
hesitate to contact us and We would be glad to assist.

Thank you for choosing Microsoft!

Best regards,
Ray Zhang
APAC/GCR 24x7 Customer Service Team
Microsoft Global Technical Support Center
Email: gtsccsa@microsoft.com
Our vision is to deliver a valued and seamless customer service and
support experience that earns the trust of our customers and
partners and positively influences their perceptions of Microsoft.

From: Norjehan.Mehdzar@shell.com
[mailto:Norjehan.Mehdzar@shell.com]
Sent: 2009 年 1 月 26 日 19:05
To: APAC/GCR 24x7 Customer Service Center; Yin Cui
Cc: Norman.Choo@shell.com
Subject: FW: SRS090125600006: [XCON] 3 other BH
servers that has queued mail only to QSR-S-01001

Hi Microsoft team/Yin Cui,

Appreciate if you could get back to us urgently as the issue
is currently occuring.  My contact no is +6012-3096272.

Thanks.

Regards,
Norjehan
Ops Messaging

-----Original Message-----
From: Mehdzar, Norjehan SITI-ITSS-EUC
Sent: 26 January 2009 18:47
To: 'Yin Cui'; Rajah, Edna R SITI-ITSS-EUC
Cc: KL Based TAM's working on Shell
Subject: RE: SRS090125600006: [XCON] 3 other BH
servers that has queued mail only to QSR-S-01001

10

Hi Yin Cui,

The issue still occurs.  Below are the screencapture of the
queue:

Kindly provide the password to upload the data to the
workspace.  Thanks.

Regards,
Norjehan

-----Original Message-----
From: Yin Cui [mailto:kylecui@microsoft.com]
Sent: 26 January 2009 10:32
To: Rajah, Edna R SITI-ITSS-EUC; Mehdzar,
Norjehan SITI-ITSS-EUC
Cc: KL Based TAM's working on Shell
Subject: SRS090125600006: [XCON] 3 other BH
servers that has queued mail only to QSR-S-01001

Dear Edna,

Thanks for contacting Microsoft Enterprise
Communication Support service. My name is Yin
Cui.  For your reference, the service request ID is
SRS090125600006.

According to your description, I understand that 3
of bridgehead servers were not able to deliver
messages to the server QSR-S-01001.

If I misunderstood your concerns, please feel free to
let me know.

I am not sure if this issue still persists. If yes, can
you please take the following action items?

1.       Note down (or capture a screen shot) of
the queue status in Exchange System
Manager. If the queue status is in Retry,
please highlight the queue and check the
detailed information of the queue status.
2.       Turn on SMTP logs on SMTP virtual server.
Please ensure that you have checked all
properties for logging. After that, let's click
Force Connection in the queue viewer. If
the status is back to retry, please send me
the latest SMTP logs for further analysis.

11

If this issue does not occur currently, we may not
have thorough data for further investigation.
However, the following information is always
helpful to understand some background
information which could be relative with the issue.

1.       MPS Report for Exchange on both the

source servers  and the destination servers.
The utility can be downloaded from:
http://download.microsoft.com/download/
b/b/1/bb139fcb-4aac-4fe5-a579-
30b0bd915706/MPSRPT_Exchange.exe

2.       If you could recall the queue status, can

you please let me know whether the queue
was in Retry or Active when the issue
occurred?

3.       If you ever turned on SMTP logs on the

source or destination servers before, can
you please collect the SMTP logs on the
servers for the date when the issue
occurred?

You can upload all the data you've collected to the
following workspace:
https://sftasia.one.microsoft.com/choosetransfer.a
spx?key=f3e5e2e4-1505-4ffb-8250-6e717e2b0aaf

If you have any questions or concerns, please feel
free to let me know. I am glad to follow up with
you.

Regards,
Yin Cui

Escalation Engineer, Enterprise Communication Support
Team
Commercial Technical Support Enterprises
APGC Customer Service & Support

Mailto: kylecui@microsoft.com
Phone:86-21-61514571
Australia Toll Free: 1800800142
New Zealand Toll Free: 0800442128

Delighting our customers is our #1 priority.
We welcome your comments and suggestions about how we can
improve the support we provide to you. You can also contact my
manager, Jeff Chen at (86-21)6469-1188 ext. 4349 or by sending email
to: jeffchen@microsoft.com.

12

