# Personal Style Profile — 崔崟 (Yin Cui)

**Extracted:** 2026-07-06  
**Samples Analyzed:** 10 markdown files with content (1 empty file excluded)  
**Languages:** zh (Chinese academic), en (English technical/business email)  
**Corpus:** 1,941 Chinese sentences; 587 English sentences; ~1,802 paragraphs; ~32,000 Chinese characters + ~25,000 English words of technical prose.  
**Source documents:** doctoral thesis proposal, engineering-ethics course papers, supply-chain/energy-internet security essays, a leadership-assignment response, Microsoft support email threads, and an English XDP paper draft.

> **Data caveats:** The Chinese files were converted from PDFs with hard line breaks at ~36–40 characters, so the raw paragraph unit is a *physical line* rather than a semantic paragraph. Code blocks and table fragments in the thesis proposal inflate maxima. The statistics below are therefore interpreted as **stylistic fingerprints**, not exact paragraph counts.

---

## 1. Chinese Academic Fingerprint

### 1.1 Sentence Statistics

| Metric | Value | Interpretation |
|---|---|---|
| Mean sentence length | 25.6 characters | Medium-short; denser than textbook prose, lighter than classical academic Chinese. |
| Median | 22 characters | Half of all sentences are under 22 chars — strong short-sentence bias. |
| Std dev / CV | 37.5 / 1.46 | **Very high burstiness**: mixes terse headings, short labels, and long explanatory clauses. |
| Range | 1 – 1290 chars | The 1290-char outlier is a JSON table block in the thesis proposal; natural max is ~120 chars. |
| By document | Thesis proposal 28.6; supply-chain essay 25.0; energy-internet essay 23.6; infosec industry critique 23.8; leadership assignment 19.1; engineering ethics 21.4 | Shorter in reflective/coursework; longer in research exposition. |

**Representative short sentences:**
> "笔者结合日常工作及研究，写成此文。" (supply-chain essay, 15 chars)  
> "能源互联网的安全运行关系到国计民生，国家安全。" (energy-internet essay, 23 chars)

**Representative long sentences:**
> "以边缘计算节点为中心，将中心与相关联设备、资源等定义为边缘区域（边缘侧），形成以边缘安全区域自治，云边协同管理安全的安全治理架构（图 1）：即保证了边缘区域的安全，又兼顾了云端统一管理的需求。" (energy-internet edge security, 120 chars — one breathless clause chain)

> "本研究拟以软件定义的思想为基础，解耦访问控制控制平面和数据平面：控制平面包括认证引擎、策略引擎、通知引擎等模块负责访问控制的决策及结果下发；数据平面包括执行引擎，编排引擎等模块负责访问控制决策在各个执行点的执行。" (thesis proposal, 152 chars — colon + semicolon layering)

**Pattern:** Sentences grow when introducing a model, architecture, or mechanism. The author extends length through stacked prepositional phrases and parenthetical enumerations (`包括...等`) rather than embedded subordinate clauses.

### 1.2 Vocabulary & Register

| Dimension | Evidence |
|---|---|
| Technical density | Very high: 零信任架构, SDP, 软件定义边界, 单包认证, 设备画像, 访问控制, 僵尸网络, 供应链, 边缘计算, 物联网. |
| Formal vs. oral | Formal written Chinese. Almost no spoken fillers, no网络 slang, minimal 了 as sentence-final particle. |
| Humble framing | Titles use 浅析/浅见/浅议 (4 instances); conclusions admit 不足 (11 instances), 粗浅 (1), 很多不足之处 (2). |
| Self-reference | 笔者 (10), 本文 (3), 作者 (6), 我们 (2), 我 (41). The 我 is mostly in reflective coursework (leadership, infosec critique). |
| Top content words | 安全, 访问控制, 物联网/联网, 设备, 边缘, 能源, 供应链, 数据, 策略, 画像. |
| Function words | 的 (1,700+), 了, 在, 和, 与, 及, 等, 对, 为, 以, 通过, 因此, 从而, 此外, 同时, 一方面...另一方面. |

**Representative humble framing:**
> "本文是笔者结合日常工作和对能源互联网的粗浅理解所作，有很多不足之处。" (energy-internet essay)  
> "牛津大学的马丁·克里斯多夫教授指出：'21 世纪的竞争不是企业与企业的竞争，而是供应链与供应链的竞争'... 未雨绸缪，让信息安全技术为智慧供应链的发展保驾护航。" (supply-chain essay — cites authority then offers guardedly optimistic close)

> "信息安全产业若想实现高速度，高质量的发展，首先要注重行业引导... 二是要注重培养人才... 三是要注重知识产权保护..." (infosec critique — three numbered imperatives, no grandiosity)

**Distinctive register trait:** The author uses a **state-the-problem-with-undersell** voice. He will present a bold claim (e.g., "我国信息安全产业高速度低质量") but immediately ground it with enumerated reasons and close with modest recommendations.

### 1.3 Argument Structure

**Default macro-structure:**
1. **Background / historical context** (随着... / 自...以来 / 近年来...)
2. **Problem statement** (然而... / 但是... / 亟...)
3. **Decomposition** (one cause, two risks, three reasons, four modules)
4. **Evidence** (case studies, policy citations, technical standards, own CVE reports)
5. **Solution / proposal** (usually numbered)
6. **Conclusion** (summary + forward-looking caveat)

**Example skeleton from supply-chain essay:**
> 0. 引言 → 1. 背景 (1.1 数字化, 1.2 物联网, 1.3 安全事件) → 2. 隐患及风险 (2.1 攻击目的, 2.2 隐患分析) → 3. 安全对策 (3.1–3.5) → 4. 结束语

**Example skeleton from thesis proposal:**
> 摘要 → 第1章 背景及意义 → 第2章 文献综述 → 第3章 研究内容及方案 → 第4章 预期成果及创新点 → 第5章 总体安排

**Transitions:** Prefers explicit connectors over implicit flow. Frequent: 因此, 因而, 从而, 此外, 同时, 另一方面, 综上所述, 简言之, 具体来说, 值得注意的是, 遗憾的是.

**Excerpt showing historical-to-problem transition:**
> "自第二次工业革命以来，科技发展经历了信息化、网络化、数字化的三个发展阶段。信息化使得...网络化解决了...数字化则提供了..." → "智慧供应链在信息化、网络化、数字化的发展过程中也经历了孕育期、萌芽期和发展期三个阶段。" → "物联网的高速发展的同时也展示出更多的脆弱性和更大的受攻击面。" (supply-chain essay)

**Excerpt showing problem decomposition:**
> "信息安全产业高速度发展的原因有三：一是产业需求巨大...二是合规需求推动...三是资本市场青睐..." → "信息安全产业低质量发展原因也有三：一是...'小、散、乱'...二是抄袭者居多...三是基础研究薄弱、创新人才匮乏。" (infosec critique)

### 1.4 Paragraph Organization

- **Topic-sentence position:** Usually first. The author states the point, then elaborates with evidence or mechanism.
- **Paragraph length:** Heavily skewed by PDF line-break artifacts. Semantic paragraphs are typically 1–3 physical lines (~40–120 characters), rarely exceeding 150 characters in Chinese course papers.
- **One-paragraph-one-idea:** Strong. Each numbered sub-section contains a claim followed by a brief supporting paragraph.
- **List paragraphs:** Uses 顿号-separated item lists within sentences, and sometimes numbered bullets (1. 2. 3.) for procedures.

**Excerpt (topic-first, then support):**
> "攻击者对物联网系统的攻击目的相对传统的网络攻击更加聚焦。通常可以分为以破坏为目的的攻击、以数据窃取为目的的攻击和以欺诈获利为目的的攻击。" (supply-chain essay)

**Excerpt (list compressed into a sentence):**
> "除了有线连接之外，大量的物联终端设备使用无线通信协议，包括4G、5G、NB-IoT、Wi-Fi、蓝牙、Zigbee、LoRa、红外等都是目前较为常见的终端无线通信协议。" (supply-chain essay)

### 1.5 Punctuation Habits

| Punctuation | Share of total | Notes |
|---|---|---|
| 句号 / period | 52.4% | Sentence-final; English period also frequent. |
| 逗号 / comma | 26.0% | Chinese comma is heavy — often mid-sentence enumeration. |
| 顿号 | 6.2% | Distinctive list marker; used inside comma clauses. |
| 冒号 / colon | 7.0% | Introduces definitions, lists, equations, figure captions. |
| 分号 / semicolon | 2.0% | Rare in Chinese; used mainly in thesis proposal to separate parallel model components. |
| 引号 | 6.1% | Mostly Chinese corner quotes for citations and coined terms; English double quotes rare. |

**Punctuation signature:** The author favors **comma-driven enumeration** over semicolons. In Chinese, a single sentence often contains multiple 逗号-separated clauses ending in 句号, with 顿号 for sub-items. This creates a "breathless but controlled" cadence.

**Excerpt:**
> "物联网使得设备与设备之间具备了进行数据交换的能力，是数字化技术的重要依托；同时物联网的终端具备了对生产设备、环境、资源等信息低成本、低能耗、实时性的监控的能力，是智慧供应链上风险防范的重要技术依托之一。" (supply-chain essay — semicolon used to contrast two capabilities, then comma chains within each side)

### 1.6 Heading Style

- **Chinese papers:** Numbered decimal hierarchy: `0. 引言`, `1. 背景`, `1.1. 数字化带来...`, `1.2. ...`, `2.1.1. 以破坏为目的...`.
- **Thesis proposal:** Uses `第 X 章` + decimal subsections (`第 1 章 选题的背景及意义`, `2.1 基于属性的访问控制`).
- **Course papers:** Often use `一、`, `二、`, `1、`, `2、` or decimal headings.
- **Headings are noun phrases**, not questions or imperative verbs: `安全现状`, `物联网的安全隐患`, `安全对策及建议`.

**Representative headings:**
> `1. 背景` → `1.1. 能源互联网发展` → `1.2. 能源互联网的相关技术` → `1.3. 能源互联网的安全风险` → `1.4. 本章小节` (energy-internet essay)

> `第 2 章 文献综述` → `2.1 基于属性的访问控制` → `2.2 基于能力的访问控制` → `2.3 软件定义安全` → `2.4 身份` → `2.5 小结` (thesis proposal)

### 1.7 Openings & Closings

**Openings:**
- **Context-first**, rarely hook-first. Common opening moves:
  - "随着..." (as X develops)
  - "自...以来" (since...)
  - "笔者近日聆听了...讲座..." (personal trigger)
  - "进入新世纪后..." (broad historical)

**Excerpt openings:**
> "笔者近日聆听了刘大成教授关于《数字化时代全球产业链及供应链变革》的讲座，深切体会到了数字化为全球经济及供应链带来的发展。" (supply-chain essay)  
> "高速发展的物联网技术深入到生产生活的各处，带来便利的同时，也引发了人们对安全的担忧。" (thesis proposal)  
> "进入新世纪后，我国信息产业突飞猛进。" (infosec critique)

**Closings:**
- **Summarize + caveat + forward look.** Often ends with a restraint phrase: 任重道远, 还有很多不足之处, 需要持续优化.
- **Call to action is understated**, usually framed as "需要关注" or "应..." rather than a rallying cry.

**Excerpt closings:**
> "能源互联网信息安全建设，任重道远。" (energy-internet essay)  
> "在发展智慧供应链体系的同时，必须同步考虑到的数字化时代新的技术所带来的新的安全风险。未雨绸缪，让信息安全技术为智慧供应链的发展保驾护航。" (supply-chain essay)  
> "作答完毕！" (leadership assignment — the only exclamation mark in the Chinese corpus; a deliberate, human sign-off)

### 1.8 Person & Voice

| Form | Count | Usage |
|---|---|---|
| 我 | 41 | Coursework, reflective critique, leadership analysis. |
| 笔者 | 10 | Formal papers; self-reference without using first person. |
| 笔者认为 | 2 | Explicit claim-ownership in the infosec critique. |
| 本文 | 3 | Referring to the paper itself. |
| 我们 | 2 | Rare; used in engineering-ethics paper for shared professional stance. |
| 作者 | 6 | Mostly in citations, not self-reference. |

**Voice pattern:** The author keeps himself **off-stage in technical papers** and **on-stage in reflective coursework**. In formal Chinese he uses 笔者; in reflective pieces he uses 我 with direct judgment.

**Excerpt (formal, 笔者):**
> "笔者认为，信息安全产业高速度发展的原因有三..." (infosec critique)  
> "笔者就曾经向 CNVD 报告了某智慧门禁系统在网络失效后的应急开门功能的逻辑漏洞(CNVD-2019-19059)。" (supply-chain essay — personal evidence inserted as credibility marker)

**Excerpt (reflective, 我):**
> "讨论一个人的情商水平，我认为需要分析这个人所处的背景条件。" (leadership assignment)  
> "基于以上分析，我认为，阿方索最重要也是最紧迫的提升就是学习感知自己的情绪..." (leadership assignment)

---

## 2. English Fingerprint

### 2.1 Sentence Structure

| Metric | Value | Notes |
|---|---|---|
| Mean sentence length | 9.3 words | Short; even shorter than typical business English. |
| Median | 8 words | Half of sentences are under 8 words — many fragments and headings. |
| Std dev / CV | 8.5 / 0.91 | High burstiness, driven by email fragments and technical labels. |
| Range | 1 – 53 words | One-word sentences are mostly email fragments / table cells. |
| Passive indicators | 42 | Concentrated in the XDP paper (22) and support emails (20). |
| Active first person | 50 | Mostly in emails (I/we) rather than the paper. |

**Short English sentences (email fragments):**
> "Thanks for the reply."  
> "Regards,"  
> "Welcome."

**Long English sentences (XDP paper):**
> "In this paper, by leveraging a pure XDP approach, we present the design of the reconfigurable switch which provides the abilities to program and orchestrate functional modules to implement not only functions like traditional switches but also access control from layer 2 through layer 7." (XDP paper, 43 words — long relative to the author's English mean)

> "Despite the increasing investment in Cyber security, security incidents occurred continuously." (XDP paper)

**Pattern:** English sentences are **shorter and more fragmentary** than Chinese. The XDP paper, despite being academic, averages only 7.0 words/sentence because of the PDF line-break artifact and many one-word labels. The natural English sentence length in the body is probably ~12–18 words — still compact.

### 2.2 Vocabulary & Register

- **Technical density:** Very high. Top English terms: control, access, abac, internet, iot, based, sdp, security, network, gateway, xdp, lateral, movement, mqtt, ieee, sdn, rbac, policy, capability, ddos.
- **Academic vs. casual:** Academic in the XDP paper; business-formal in emails. No contractions, no slang, minimal idioms.
- **L1 interference markers:**
  - Missing articles: "the board is not as clear as old-time", "new protection philosophies are raised up"
  - Article overuse/underuse: "the AI are introducted" (subject-verb agreement + article)
  - Noun stacking: "cyber security", "access control ability", "security mechanism of firewalls"
  - Verb choice: "raises up", "introducted", "orcheater" (typo but consistent with Chinese phonetic transposition)

**Excerpt (technical density):**
> "XDP (eXpress Data Path) is a high performance and programmable data path technology, which operates at the early stage of the network driver, so it can process network packets before they reach the Linux kernel stack." (XDP paper)

**Excerpt (L1 interference):**
> "Even the AI are introducted into cyber security domain to help people analyze the data and logs to identify the potential attacks or security breaches." (XDP paper — missing article, verb agreement, tense)

### 2.3 Article / Tense Patterns

- **Articles:** Inconsistent. The author often omits articles where standard English requires them, especially before abstract nouns and domain names (`cyber security domain`, `industrial environments`).
- **Tense:** Mixes present and past within the same paragraph. In the XDP paper, background facts are given in present tense (`XDP is...`), but recent events use past tense (`security incidents occurred continuously`). The abstract shifts from present (`bring`) to past (`occurred`) to present (`demonstrate`) within three sentences.
- **Verb forms:** Occasional misuse of past participles as adjectives or verbs (`introducted`, `raised up`).

**Excerpt showing tense/article drift:**
> "New technologies bring benefits to life and work as well as security threats and risks. Despite the increasing investment in Cyber security, security incidents occurred continuously. Lack of effective lateral movement identifying and controlling is a major cause. In this paper, by leveraging a pure XDP approach, we present the design..." (XDP abstract)

### 2.4 Citation Style

- **Chinese papers:** Numbered bracket citations `[1]`, `[2]` placed at the end of sentences or after key claims. References list at the end with Chinese and English entries mixed.
- **English paper:** No formal citations in the extracted draft beyond hyperlinked URLs and a few inline references (`Barracuda reports...`, `Research showed...`). Comments indicate future citations (`批注 [KC2]: This article will be referred further...`).
- **Integration style:** Claims are made first, then supported by citation. Example: `...造成乌克兰国内大面积停电[2].` (claim + citation, not citation-driven claim).

**Excerpt:**
> "2015 年的乌克兰停电事件被认为是首次由网络攻击导致的电力中断事件，攻击者利用漏洞，通过 SCADA 系统直接下达断电控制指令，并结合电话拒绝服务攻击，有意的延缓运维进度，造成乌克兰国内大面积停电[2]。" (supply-chain essay)

---

## 3. Email Register

### 3.1 Formality Level

- **Business-formal, support-engineer style.**
- No contractions in the extracted Microsoft support threads.
- Uses full names and titles: `Yin Cui`, `Escalation Engineer`, `Enterprise Communication Support Team`.
- Abbreviations are technical, not casual: `IU`, `RU`, `MSP`, `KB`, `SMTP`, `BLOB`, `Netmon`, `SPA`, `TLS`.

### 3.2 Structure

- **Openings:** `Dear [Name],`, `Hi [Name],`, `Hi,`.
- **Closings:** `Thanks & Regards,`, `Regards,`, `Best regards,`, followed by full signature block.
- **Instruction format:** Strongly numbered. Uses `1.`, `2.`, `a.`, `b.`, `c.` and call-out boxes (`NOTE:`).
- **Status reporting:** Uses headers `Symptoms:`, `Cause:`, `Resolution:` with underlined separators (`=========`).

**Excerpt (Email.md — process instructions):**
> "For any IU you need, please contact me and I will help you copy it to \\sha-kylecui-08\buddy. SN.exe has been shared there as well. I will put this email to the folder in case you won't keep it." → "NOTE: This Interim Update is only for RUX (where X means the targeting RU of your IU) for Exchange 2007 SP1 (or RTM)." → "1. Download the Interim Update and the sn.exe utility... 2. To implement the update, please perform the following steps. a. ... b. ... c. ..."

**Excerpt (mail2 — support case summary):**
> "Based on your confirmation, I am going ahead to close this case. For your records, I summarized the key points below: Symptoms: ========= Messages from AMSDC1-s-03326 to QSR-S-01001 were stuck in the remote delivery queue. Cause: ====== Exchange server will send x-exps BLOB for authentication... Resolution: ========= Your network team re-configured the device to bypass all email traffics and resolved the issue."

### 3.3 Tone

- **Collaborative and service-oriented.** Frequent "please", "feel free to", "I am glad to", "thanks for your patience".
- **Authoritative on technical facts** but **deferential on customer decisions**: "If I misunderstood your concerns, please feel free to let me know."
- **Cautious:** Uses "probably", "appears that", "a potential workaround", "if yes, can you please..." rather than absolute statements.

**Excerpt:**
> "If you require further assistance regarding this issue, please feel free to write to me directly with any supplemental information. The issues will then be reopened and forwarded back to me for follow-up. I am happy to be of assistance." (mail2)

---

## 4. Cross-Lingual Patterns

### 4.1 Shared Fingerprints

| Trait | Chinese | English |
|---|---|---|
| **Hierarchical numbering** | `1. 1.1. 2.1.1.` | `1. a. b. c.` |
| **Enumerative connectors** | 首先...其次...再者...此外...最后 | First...Second...Third...Besides that...Finally |
| **Problem-first structure** | 背景 → 问题 → 分析 → 对策 | Background → problem → analysis → solution |
| **Formal, technical register** | 无口语，无网络梗 | No contractions, no slang |
| **Self-effacing conclusions** | 不足, 任重道远 | "If you have any questions or concerns" / "future research" |
| **Case-study evidence** | 乌克兰停电, Mirai, Dyn, 委内瑞拉 | same cases imported into English paper |

### 4.2 Thinking Style

**Problem → Decomposition → Mechanism → Caution.**

In both languages, the author moves from a broad issue to a set of sub-problems, then proposes a technical or organizational mechanism, and ends with a caveat about limitations or future work. This is the dominant rhetorical fingerprint across all documents.

**Example in Chinese:**
> 能源互联网发展 → 安全风险 → 云、管、边、端架构 → 边缘安全区域自治 → 四个模块 → 预期效果 + 仍需完善

**Example in English (XDP paper):**
> New technologies → lateral movement risk → traditional firewall/EDR limitations → reconfigurable switch based on XDP → three abilities → prototype + performance → future research

### 4.3 Distinctive Phrases (Favored Across Documents)

| Phrase | Context | Why it matters |
|---|---|---|
| "随着...的发展/丰富/增加" | Chinese openings | Preferred historical-context opener |
| "一方面...另一方面..." | Chinese contrast | Balanced, two-sided analysis |
| "一是...二是...三是..." | Chinese enumeration | Strong enumeration signature |
| "因此..." / "因而..." / "从而..." | Chinese transitions | Explicit causality |
| "亟待..." / "亟..." | Chinese problem statements | Formal urgency without panic |
| "任重道远" | Chinese conclusions | Signature modest close |
| "cloud-pipe-edge-end" / "云、管、边、端" | Both languages | Author's conceptual anchor for IoT architecture |
| "zero trust" / 零信任 | Both languages | Recurring security lens |
| "please feel free to..." | English email | Polite, deferential closing of requests |
| "Thanks & Regards" / "Regards" | English email | Consistent sign-off |

---

## 5. AI Distinguishability — What Makes This Writing Human

### 5.1 Human Irregularities

1. **CV-driven burstiness:** Chinese sentence CV = 1.46. This is far above typical AI-generated prose (CV usually 0.3–0.6). The mix of short labels, medium explanations, and occasional long mechanism descriptions creates a jagged rhythm that AI tends to smooth out.

2. **L1 transfer artifacts in English:** Missing articles, verb agreement slips, and tense shifts are strong human signals. AI models trained on native English rarely produce "the AI are introducted" or "security incidents occurred continuously" in this context.

3. **Personal evidence inserted in formal prose:** The author drops in `笔者就曾经向 CNVD 报告了...` in the middle of a technical analysis. AI would either omit this or wrap it in a more detached footnote.

4. **Inconsistent formatting:** The Chinese files have line-break artifacts, mixed punctuation spacing, and occasional typos (`千机一密` vs `千机一密`, `称为了` vs `成为了`). AI output is usually typographically uniform.

5. **Domain-specific case curation:** The same cases (Ukraine blackout 2015, Mirai 2016, Venezuela 2019) recur across multiple Chinese papers and the English paper, suggesting a personal knowledge base rather than generated boilerplate.

6. **Emotional punctuation outlier:** The only exclamation mark in the Chinese corpus is `作答完毕！` at the end of a course assignment. This is a deliberate, human sign-off.

7. **Humble markers in titles and conclusions:** `浅析`, `浅见`, `浅议`, `不足之处`, `任重道远` appear repeatedly. AI tends to overuse confidence phrases or avoid such modesty.

### 5.2 Burstiness (Sentence Length Variance)

| Corpus | Mean | Median | CV | Human verdict |
|---|---|---|---|---|
| Chinese academic | 25.6 | 22 | 1.46 | **High burstiness** — very human. |
| English XDP paper | 7.0 | 7 | 0.66 | Moderate (artifact-low due to line breaks). |
| English support emails | 12.3 | 10 | 0.87 | High burstiness due to fragments and long summaries. |
| Email.md instructions | 8.1 | 8 | 0.91 | High — mix of one-word labels and full procedural sentences. |

### 5.3 Vocabulary Surprise

- **Unexpected word choices:**
  - "拥有目标设备" (to "own" a target device) — informal verb repurposed formally.
  - "细胞级" (cell-level) for device-level security — bio metaphor unusual in cybersecurity.
  - "千机一密" (one key for a thousand devices) — coined, idiomatic compression.
  - "保驾护航" (escort and protect) — idiomatic close.
  - "管而不控" / "不管不控" — parallel rhyming neologisms.
  - "old-time" (English) instead of "the old days" — non-native but distinctive.

- **Predictable AI patterns that are absent:**
  - No "In conclusion," / "In summary," formulaic closes in Chinese.
  - No "It is important to note that..." padding.
  - No "delve into", "robust", "leverage", "seamless" AI buzzwords in English.
  - No emoji or markdown formatting beyond headings and numbered lists.

---

## 6. Do / Don't List for a Style Rewriter

### DO

- Use **hierarchical numbered headings** (`1.`, `1.1.`, `2.1.1.`) for technical documents.
- Start Chinese academic pieces with **historical context** (`随着...`, `自...以来`, `近年来...`).
- Decompose arguments into **enumerated lists** (`一是...二是...三是...`, `首先...其次...最后...`).
- Use **topic-first paragraphs** with one claim per paragraph.
- Insert **case-study evidence** from the author's own domain (Ukraine blackout, Mirai, Venezuela, CNVD-2019-19059, BeyondCorp, NIST SP 800-207).
- Use **humble framing** in titles and conclusions: `浅析`, `浅见`, `不足之处`, `任重道远`.
- Prefer **formal self-reference** (`笔者`, `本文`) in research papers; use `我` only in reflective/coursework pieces.
- Use **顿号** for Chinese item lists and **comma chains** for clause enumeration.
- End Chinese conclusions with a **forward-looking caveat** rather than a triumphal statement.
- In English technical writing, keep sentences **short to medium** (10–20 words) and use **First/Second/Third/Besides that** connectors.
- In English emails, use **numbered steps**, `NOTE:` callouts, and sign-offs with `Regards,` / `Thanks & Regards,`.
- Retain **L1-influenced article/tense quirks** if the goal is to sound like the user (e.g., omit some articles, use `occur` in past tense for recent events, use `raise up` instead of `raise`).
- Use **domain-specific acronym density** (XDP, eBPF, SDP, ZTNA, ABAC, RBAC, SIEM, IEC60870-5-104, MQTT, NFQUEUE, etc.).

### DON'T

- Don't use **flowery rhetoric** or motivational slogans (`赋能`, `普惠`, `拔高`, `立体认知`). The author's tone is restrained and problem-driven.
- Don't write long, balanced paragraphs of 200+ characters in Chinese. Keep semantic paragraphs under 120 characters when possible.
- Don't use **semicolons** in Chinese; the author uses 逗号 and 顿号 instead.
- Don't overuse **we** in English academic writing; the author uses `we` sparingly and often writes in a passive/institutional voice.
- Don't produce **AI-generic abstract phrases** like "This paper delves into the robust landscape of..." or "leverage cutting-edge technologies".
- Don't use **contractions** or casual email closings (`Cheers`, `Best`) in the Microsoft-style support emails.
- Don't end Chinese academic pieces with a grand claim without a caveat (`综上所述` should be followed by a limitation or future step).
- Don't use **first-person plural we** in Chinese research papers; the author almost never does.
- Don't force **perfect English grammar** if the goal is to match the user's voice — the irregularities are part of the fingerprint.
- Don't use **exclamation marks** in Chinese academic writing; the only one in the corpus is a deliberate coursework sign-off.

---

## 7. Per-Document Quick Reference

| Document | Register | Key fingerprint |
|---|---|---|
| 2020319153-崔崟-开题报告.md | Chinese doctoral thesis proposal | Longest, most formal, `第 X 章` headings, heavy English technical terms mixed in, JSON/figure artifacts, passive/institutional voice. |
| 崔崟_2020319053_数字化时代智慧供应链的信息安全风险浅析.md | Chinese academic essay | `0. 引言` → `4. 结束语`, supply-chain case studies, 浅析 in title, 未雨绸缪 close. |
| 能源互联网信息安全风险分析及浅见.md | Chinese academic essay | 浅见 in title, energy-internet focus, 云管边端 architecture, 任重道远 close. |
| 2020319153_崔崟_能源互联网边缘安全区域自治技术研究与应用.md | Chinese research proposal | ZTNA/SDP deep dive, edge-security modules, 云边协同, patent/paper output plan. |
| 工程伦理_崔崟_浅议智能手机应用中用户隐私保护的工程伦理问题.md | Chinese ethics coursework | 浅议 in title, stakeholder diagrams, legal citations, ends with 科技向善. |
| 2020319153_崔崟_浅论信息安全产业高速度低质量发展的原因.md | Chinese reflective critique | Most personal (我/笔者认为), tripartite cause analysis, blunt industry diagnosis. |
| 2020319153_崔崟_领导与沟通作业.md | Chinese leadership coursework | Shortest sentences, direct 我, 作答完毕！ sign-off, workflow advice. |
| Reconfigurable_Switch_A_Pure_XDP_Design_and_Implementation.md | English technical paper draft | L1-influenced grammar, high passive voice, Mirai/Ukraine cases, incomplete sections with `// todo:`. |
| Email.md | English business instructions | Short, numbered steps, `NOTE:` callouts, `Regards, Yin`. |
| mail2.md | English support-engineer correspondence | Longer case threads, `Symptoms/Cause/Resolution`, deferential tone, `Thanks & Regards`. |
| Mail - Kyle Cui - Outlook.md | Empty | No content; excluded from analysis. |

---

*Profile generated by quantitative analysis (sentence lengths, punctuation, vocabulary, person markers) plus manual excerpt review. Use this as a rewrite guide: when in doubt, prefer shorter sentences, enumerated structure, formal humility, and technical precision.*
