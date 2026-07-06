Kyle Cui

发件人:
发送时间:

收件人:
主题:

重要性:

Yin Cui
2008年12月10日星期三 11:00
APGC GCR BizApps ECS (All)
Steps to Apply Interim Update

高

I understand that some of you may still not understand what the Interim Update is and what steps we should take
for customers to apply an Interim update. I am sending this email to share a template for you with the necessary
steps.

For any IU you need, please contact me and I will help you copy it to \\sha-kylecui-08\buddy. SN.exe has been
shared there as well. I will put this email to the folder in case you won’t keep it.

Regards,
Yin

Hi XXX,

Thanks for your patience in waiting for the response. We now have the Interim Update ready on this case. Please
refer to the process below to apply it on the affected servers.

NOTE: This Interim Update is only for RUX (where X means the targeting RU of your IU) for Exchange 2007 SP1 (or
RTM).

1. Download the Interim Update and the sn.exe utility from the following workspace:
<your workspace>
Password: <password>
NOTE: There are two files that you need to download. Please copy them to all <server role, where you need this IU)
servers.

Exchange2007-KBxxxxxx-x64-EN.msp
Sn.exe

2. To implement the update, please perform the following steps.

a. Copy SN.exe to c:\windows.
b. Run sn.exe -Vr * to disable strong name verification.

c. Run sn.exe -Vl to verify that strong name verification is disabled

1

d. Run the Exchange2007-KBxxxxxx-x64-EN.msp file to install the update.

NOTE: Steps to remove the Interim Update:

1. Uninstall Interim Update for Exchange 2007 (KBxxxxxx) from Add/Remove programs.
2. Run sn.exe -Vu * to enable strong name verification.
3. Run sn.exe -Vl to verify that strong name verification is enabled.

Let me know if you have any concerns.

Thanks & Regards,
Yin

2

