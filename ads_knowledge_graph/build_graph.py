#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a knowledge graph of the Ads-related papers in this repository.

Inputs : ../README.md (the curated paper index)
Outputs: knowledge_graph.json  (nodes + edges)
         index.html            (self-contained interactive viewer)
         README.md             (methodology, kept hand-written)

Curation rules for "Ads-related":
  1) title explicitly mentions ads / advertising / sponsored / display advertising
  2) title is a CTR/CVR/conversion prediction paper deployed on an ads business
     (Alibaba display ads, Meta/Facebook ads, Google ads, Kuaishou ads, Sina Weibo
     ads, Baidu, Tencent, JD, Meituan, Criteo, Twitter, eBay, Kuaishou, Bytedance ad rec)
  3) delayed-feedback conversion attribution family
  4) ranking-model calibration for ads systems
  5) surveys covering online advertising
Paper -> paper "builds on" edges are manually curated from the literature.
"""
import json, re, os, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---------------------------------------------------------------- parse README
entries = []
section = sub = ""
for ln in open(os.path.join(ROOT, "README.md"), encoding="utf-8").read().split("\n"):
    if ln.startswith("## ") and not ln.startswith("####"):
        section, sub = ln[3:].strip(), ""
    elif ln.startswith("#### "):
        sub = ln[5:].strip()
    elif ln.startswith("* ["):
        m = re.match(r"\*\s*\[(.*?)\]\((.*?)\)", ln)
        if m:
            entries.append({"section": section, "sub": sub, "title": m.group(1), "url": m.group(2)})

def norm(s):
    return re.sub(r"\s+", " ", s.replace("\u2019", "'").replace("\u2018", "'")).strip().lower()

# unique papers (same title listed in several sections -> one node, sections merged)
unique = {}
for e in entries:
    k = norm(e["title"])
    if not k:
        continue
    if k in unique:
        unique[k]["sections"].append((e["section"], e["sub"]))
    else:
        e["sections"] = [(e["section"], e["sub"])]
        unique[k] = e

def stars_of(title):
    runs = re.findall(r"\*+", title)
    return max((len(r) for r in runs), default=0)

# ---------------------------------------------------------------- hubs
STAGES = {  # id -> (label, color, description)
    "survey":     ("Survey & Systems",       "#94a3b8", "Surveys and production-system retrospectives that span the ads pipeline."),
    "retrieval":  ("Ads Retrieval",          "#38bdf8", "Matching / retrieval: finding candidate ads for a query or user request."),
    "prerank":    ("Pre-Ranking",            "#a78bfa", "Cheap scoring stage that prunes candidates before fine ranking."),
    "ctr":        ("CTR Ranking",            "#34d399", "Fine ranking: click-through-rate prediction models for ads."),
    "cvr":        ("CVR & Conversion",       "#fbbf24", "Post-click conversion-rate estimation: entire-space and multi-task modeling."),
    "delayed":    ("Delayed Feedback",       "#f87171", "Conversions arrive long after clicks - unbiased modeling under label delay."),
    "calibration":("Calibration",            "#fb923c", "Keeping predicted probabilities consistent with real outcomes for bidding & ranking."),
    "relevance":  ("Relevance",              "#e879f9", "Query-ad / item relevance modeling for search ads."),
    "generative": ("Generative & Unified",   "#22d3ee", "LLM and generative-retrieval paradigms that unify the ads pipeline."),
}
THEMES = {  # id -> (label, description)
    "seq":     ("Attention & Behavior Sequence", "User behavior / interest modeling: DIN and its descendants."),
    "feat":    ("Feature Interaction & Crossing","Explicit feature crossing: FM lineage, DCN, gating, co-action."),
    "mtl":     ("Multi-task & Entire Space",     "Multi-task learning and entire-space estimation."),
    "domain":  ("Multi-domain & Multi-scenario", "One model serving many domains / scenarios / ad types."),
    "genllm":  ("Generative & LLM",              "Large language models and generative retrieval for ads."),
    "distill": ("Knowledge Distillation",        "Compressing large/privileged teachers into serving models."),
    "scaling": ("Scaling Laws & Foundation",     "Scaling behavior and foundation models for ads ranking."),
    "mm":      ("Multimodal",                    "Visual / multimodal signals in ads CTR and relevance."),
    "gnn":     ("Graph Neural Networks",         "Graph-based intention / behavior modeling."),
    "system":  ("System & Infrastructure",       "Serving systems, memory, and industrial engineering."),
    "debias":  ("Debiasing & Sample Selection",  "Selection bias and causal debiasing for conversion estimation."),
}
COMPANIES = {  # name shown -> normalized id
    "Alibaba":"alibaba", "Meta":"meta", "Google":"google", "Tencent":"tencent",
    "Kuaishou":"kuaishou", "Baidu":"baidu", "JD":"jd", "Meituan":"meituan",
    "Sina":"sina", "Criteo":"criteo", "Twitter":"twitter", "Huawei":"huawei",
    "Bytedance":"bytedance", "eBay":"ebay", "Yahoo":"yahoo", "Coupon":"coupon",
}
COMPANY_LABEL = {"meta":"Meta / Facebook", "twitter":"Twitter / X", "jd":"JD.com", "coupon":"Coupon (search)"}

VENUES = {"KDD","WWW","SIGIR","CIKM","RecSys","AAAI","IJCAI","WSDM","NeurIPS","arXiv","ADKDD","TOIS","TIST","DLP-KDD","SIGWEB"}
VENUE_FIX = {"NIPS":"NeurIPS","Recsys":"RecSys","AdKDD":"ADKDD","Arxiv":"arXiv","DLP-KDD":"DLP-KDD","Sigweb":"SIGWEB","Arixiv":"arXiv"}

# ---------------------------------------------------------------- curated ads papers
# (key, unique-title substring, tag, year, company, venue, stage, [theme ids], note)
PAPERS = [
 # ---- surveys / systems ----
 ("dltr","deep learning to rank in industrial search engines","DLTR",2026,None,"TOIS","survey",[],"Repo's own TOIS 2026 overview of DLTR in search, rec & advertising."),
 ("rlsurvey","deep reinforcement learning for search, recommendation, and online advertising","RL-Survey",2019,None,"SIGWEB","survey",[],"Survey of deep RL across the three industries."),
 ("factory","on the factory floor","Factory Floor",2023,"Google","arXiv","survey",["system","scaling"],"ML engineering practice for industrial-scale ads models at Google."),
 # ---- retrieval / matching ----
 ("mobius","mobius - towards the next generation","MOBIUS",2019,"Baidu","KDD","retrieval",[],"Bi-tower query-ad matching keeping recall relevant for CTR in Baidu sponsored search."),
 ("rare","real-time ad retrieval via llm-generative commercial intention","RARE",2025,"Tencent","arXiv","retrieval",["genllm"],"LLM-generative commercial intention for real-time ad retrieval in sponsored search."),
 ("adgpu","an efficient embedding based ad retrieval","GPU-Ad-Retrieval",2025,"Tencent","arXiv","retrieval",["feat"],"Embedding-based ad retrieval with GPU-powered feature interaction."),
 ("gin","graph intention network","GIN",2019,"Alibaba","SIGIR","retrieval",["gnn"],"Graph intention network for CTR prediction in sponsored search."),
 ("gr4ad","generative recommendation for large-scale advertising","GR4AD",2026,"Kuaishou","arXiv","generative",["genllm"],"Generative recommendation for large-scale advertising."),
 # ---- pre-ranking ----
 ("copr","copr - consistency-oriented pre-ranking","COPR",2023,"Alibaba","CIKM","prerank",[],"Consistency between pre-ranking and ranking for online advertising."),
 # ---- CTR ranking: foundations ----
 ("lrftrl","ad click prediction - a view from the trenches","LR-FTRL",2013,"Google","KDD","ctr",["feat"],"FTRL-proximal online LR for ads CTR at Google - the classic production click model."),
 ("fblessons","practical lessons from predicting clicks","FB-Lessons",2014,"Meta","ADKDD","ctr",[],"GBDT+LR feature engineering & calibration lessons from Facebook ads."),
 ("lrdisplay","simple and scalable response prediction","LR-Display",2014,"Yahoo","TIST","ctr",["feat"],"Layered LR feature model for display-ads response prediction."),
 ("twitterctr","click-through prediction for advertising in twitter timeline","TW-CTR",2015,"Twitter","KDD","ctr",[],"Ads CTR prediction in the Twitter timeline."),
 ("deepintent","deepintent - learning attentions for online advertising","DeepIntent",2016,"Criteo","RecSys","ctr",["seq"],"RNN attention over ad/display context for online advertising."),
 ("ffm","field-aware factorization machines","FFM",2016,"Criteo","RecSys","ctr",["feat"],"Field-aware FM - Criteo display-ads CTR competition winner."),
 ("dcn","deep & crossnetwork for ad click predictions","DCN",2017,"Google","ADKDD","ctr",["feat"],"Explicit feature crossing network for Google ads CTR."),
 ("deepfm","deepfm - a factorization-machine based neural network","DeepFM",2017,"Huawei","IJCAI","ctr",["feat"],"FM + DNN with shared embeddings for CTR."),
 ("fgcnn","feature generation by convolutional neural network","FGCNN",2019,"Huawei","WWW","ctr",["feat"],"CNN-generated auxiliary features for CTR."),
 # ---- DIN family / sequence modeling ----
 ("din","deep interest network for click-through rate prediction","DIN",2018,"Alibaba","KDD","ctr",["seq"],"Attention over user behaviors - Taobao display ads CTR."),
 ("dien","deep interest evolution network","DIEN",2019,"Alibaba","AAAI","ctr",["seq"],"Interest evolution with GRU + attention (AUGRU)."),
 ("dsin","deep session interest network","DSIN",2019,"Alibaba","IJCAI","ctr",["seq"],"Session-split interest modeling with self-attention."),
 ("dstn","deep spatio-temporal neural networks","DSTN",2019,"Alibaba","KDD","ctr",["seq"],"Auxiliary contextual ads & spatio-temporal signals for CTR."),
 ("dhan","deep interest with hierarchical attention network","DHAN",2020,"Alibaba","SIGIR","ctr",["seq"],"Hierarchical attention over behaviors."),
 ("mimn","practice on long sequential user behavior modeling","MIMN",2019,"Alibaba","KDD","ctr",["seq","system"],"Memory network + UIC server for lifelong behaviors in production CTR."),
 ("sim","search-based user interest modeling","SIM",2020,"Alibaba","arXiv","ctr",["seq"],"Two-stage hard search over lifelong behavior data for CTR."),
 ("eta","efficient long sequential user data modeling","ETA",2022,"Alibaba","arXiv","ctr",["seq"],"SimHash retrieval of relevant behaviors - efficient lifelong sequence modeling."),
 ("ubr4ctr","user behavior retrieval for click-through rate prediction","UBR4CTR",2020,None,"SIGIR","ctr",["seq"],"Retrieval-style relevant-behavior selection for CTR."),
 ("sdim","sampling is all you need on modeling long-term","SDIM",2022,"Meituan","CIKM","ctr",["seq"],"Hash-sampling of long-term behaviors for CTR."),
 ("twin","twin - two-stage interest network","TWIN",2023,"Kuaishou","arXiv","ctr",["seq"],"End-to-end lifelong behavior modeling with consolidated twin towers at Kuaishou ads."),
 ("twin2","twin v2 - scaling ultra-long","TWINv2",2024,"Kuaishou","CIKM","ctr",["seq","scaling"],"Ultra-long behavior sequence modeling for CTR at Kuaishou."),
 ("kfatt","kalman filtering attention","KFAtt",2020,"JD","NeurIPS","ctr",["seq"],"Kalman-filtering attention for user behavior modeling in CTR."),
 ("racp","contextualized page-wise feedback","RACP",2022,"Alibaba","WSDM","ctr",["seq"],"Page-wise contextual feedback modeling for e-commerce search CTR."),
 ("jdimplicit","implicit user awareness modeling via candidate items","Implicit-UA",2022,"JD","WWW","ctr",["seq"],"Candidate-aware user modeling for CTR in search ads."),
 ("iui","iui - intent-enhanced user interest modeling","IUI",2023,"JD","CIKM","ctr",["seq"],"Intent-enhanced interest modeling for CTR."),
 ("dcin","deep context interest network","DCIN",2023,"Meituan","CIKM","ctr",["seq"],"Deep context + interest modeling for CTR at Meituan."),
 ("dihn","deep interest highlight network","DIHN",2022,"Alibaba","WWW","ctr",["seq"],"Interest highlighting for trigger-induced recommendation ads."),
 ("lrea","efficient long sequential low-rank adaptive attention","LREA",2025,"Alibaba","arXiv","ctr",["seq"],"Low-rank adaptive attention for very long sequences in CTR."),
 ("bahe","breaking the length barrier","BAHE",2024,"Alibaba","arXiv","ctr",["seq","genllm"],"LLM-encoded long textual behaviors for CTR with split encoding."),
 ("dhen","dhen - a deep and hierarchical ensemble network","DHEN",2022,"Meta","arXiv","ctr",["scaling","feat"],"Deep & hierarchical ensemble network for large-scale CTR at Meta."),
 ("est","est - towards efficient scaling laws","EST",2026,"Alibaba","arXiv","ctr",["scaling"],"Efficient scaling laws in CTR prediction via unified modeling."),
 ("srp4ctr","srp4ctr","SRP4CTR",2024,"Meituan","arXiv","ctr",["seq"],"Sequential-recommendation pre-training to enhance CTR prediction."),
 ("hyformer","hyformer - revisiting the roles","HyFormer",2026,"Bytedance","arXiv","ctr",["seq","feat"],"Unifying sequence modeling and feature interaction in one transformer for CTR."),
 ("tm20k","teacher retains full tokens","TM20K",2026,"Bytedance","arXiv","ctr",["seq","distill"],"10k-sequence modeling with token-merging distillation for e-commerce ad recommendation."),
 # ---- feature interaction / gating ----
 ("fibinet","fibinet - combining feature importance","FiBiNET",2019,"Sina","RecSys","ctr",["feat"],"SENet feature importance + bilinear interactions for Weibo ads CTR."),
 ("gatenet","gatenet - gating-enhanced deep network","GateNet",2020,"Sina","arXiv","ctr",["feat"],"Feature-level gating for CTR."),
 ("contextnet","contextnet - a click-through rate prediction framework","ContextNet",2021,"Sina","arXiv","ctr",["feat"],"Contextual refinement of feature embeddings for CTR."),
 ("masknet","masknet - introducing feature-wise multiplication","MaskNet",2021,"Sina","DLP-KDD","ctr",["feat"],"Instance-guided feature-wise masks for CTR."),
 ("fibinet2","fibinet++ - reducing model size","FiBiNET++",2023,"Sina","CIKM","ctr",["feat"],"Low-rank bilinear interaction layer for CTR."),
 ("canvideo","combo-attention network for baidu video advertising","CAN-Video",2020,"Baidu","KDD","ctr",["mm"],"Combo-attention for Baidu video advertising."),
 ("can","can - feature co-action network","CAN",2022,"Alibaba","WSDM","ctr",["feat"],"Parameterized co-action unit between features for Taobao display ads."),
 ("memonet","memonet - memorizing all cross features","MemoNet",2023,"Sina","CIKM","ctr",["feat"],"Multi-hash codebooks memorizing cross-feature representations."),
 ("gdcn","towards deeper, lighter and interpretable cross network","GDCN",2023,None,"CIKM","ctr",["feat"],"Improved crossed-field network for CTR."),
 ("interformer","interformer - effective heterogeneous interaction learning","InterFormer",2025,"Meta","CIKM","ctr",["feat","scaling"],"Heterogeneous feature interaction at Meta ads scale."),
 ("dmoe","de-correlated expert networks","D-MoE",2025,"Tencent","arXiv","ctr",["feat"],"De-correlated expert networks for CTR."),
 ("fat","from scaling to structured expressivity","FAT",2025,"Alibaba","arXiv","ctr",["feat","scaling"],"Rethinking transformer expressivity for CTR."),
 ("lpfs","lpfs - learnable polarizing feature selection","LPFS",2022,"Kuaishou","arXiv","ctr",["feat"],"Learnable feature selection for CTR."),
 ("gemnn","gemnn - gating-enhanced multi-task neural networks","GemNN",2021,"Baidu","SIGIR","ctr",["feat","mtl"],"Early feature fusion + multi-task gating for CTR."),
 ("deepmcp","representation learning-assisted click-through","DeepMCP",2019,"Alibaba","IJCAI","ctr",["mtl"],"Joint matching & ranking representations for CTR."),
 # ---- multi-domain / multi-scenario ----
 ("minet","minet - mixed interest network","MiNet",2020,"Alibaba","CIKM","ctr",["domain"],"Cross-domain (news feed ads) mixed interests for CTR."),
 ("star","one model to serve all","STAR",2021,"Alibaba","CIKM","ctr",["domain"],"Star topology multi-domain CTR for Alibaba display ads."),
 ("adasparse","adasparse - learning adaptively sparse structures","AdaSparse",2022,"Alibaba","CIKM","ctr",["domain"],"Learned sparsity per scenario for multi-domain CTR."),
 ("apg","apg - adaptive parameter generation","APG",2022,"Alibaba","NeurIPS","ctr",["domain"],"Scenario-conditioned parameter generation for CTR."),
 ("hc2","hybrid contrastive constraints for multi-scenario ad ranking","HC2",2023,"Alibaba","CIKM","ctr",["domain"],"Contrastive constraints across scenarios for ad ranking."),
 ("mmn","masked multi-domain network","MMN",2023,"Alibaba","CIKM","cvr",["domain","mtl"],"Multi-type multi-scenario CVR with a single model."),
 ("rec4ad","rec4ad - a free lunch","Rec4Ad",2023,"Alibaba","CIKM","ctr",["domain","debias"],"Recommendation data mitigating sample-selection bias for ads CTR."),
 ("dffm","dffm - domain facilitated feature modeling","DFFM",2023,"Huawei","CIKM","ctr",["domain","feat"],"Domain-aware feature modeling for CTR."),
 ("safi","scenario-adaptive feature interaction","Scenario-Adaptive-FI",2023,"Tencent","KDD","ctr",["domain","feat"],"Scenario-adaptive feature interaction for CTR."),
 ("mlora","mlora - multi-domain low-rank","MLoRA",2024,"Alibaba","RecSys","ctr",["domain"],"Low-rank scenario adapters for multi-domain CTR."),
 ("lcn","cross-domain lifelong sequential modeling","LCN",2024,"Tencent","KDD","ctr",["domain","seq"],"Cross-domain lifelong sequences for online CTR."),
 ("stem","ads recommendation in a collapsed and entangled world","STEM",2024,"Tencent","KDD","ctr",["domain","mtl","system"],"Tencent's production framework for collapsed multi-type ads recommendation."),
 # ---- meta / google scale ----
 ("sum","scaling user modeling","SUM",2024,"Meta","arXiv","ctr",["scaling","system"],"Large-scale online user representations for ads personalization at Meta."),
 ("exfm","external large foundation model","ExFM",2025,"Meta","arXiv","ctr",["scaling","distill","system"],"Serving trillion-parameter foundation features for online ads recommendation."),
 ("llatte","llatte - scaling laws for multi-stage","LLaTTE",2026,"Meta","arXiv","ctr",["scaling","seq"],"Scaling laws for multi-stage sequence modeling in Meta ads."),
 ("lattice","meta lattice - model space redesign","Meta-Lattice",2026,"Meta","KDD","ctr",["scaling","system"],"Lattice model-space redesign for cost-effective industry-scale ads recommendations."),
 ("rankup","rankup - towards high-rank representations","RankUp",2026,"Tencent","arXiv","ctr",["scaling","feat"],"High-rank representations for large-scale advertising recommenders."),
 # ---- CVR / conversion ----
 ("esmm","an effective approach for estimating post-click","ESMM",2018,"Alibaba","SIGIR","cvr",["mtl"],"Entire-space multi-task CVR - eliminates sample-selection bias & data sparsity."),
 ("esm2","post-click behavior decomposition","ESM2",2020,"Alibaba","SIGIR","cvr",["mtl"],"Post-click behavior decomposition (CTR -> CTCVR -> CVR)."),
 ("causaldebias","large-scale causal approaches to debiasing","Causal-Debias",2020,"Alibaba","WWW","cvr",["mtl","debias"],"Causal debiasing of post-click conversion estimation."),
 ("hm3","hierarchically modeling micro and macro","HM3",2021,"Alibaba","SIGIR","cvr",["mtl","seq"],"Micro & macro behaviors via multi-task learning for CVR."),
 ("meituanconv","modeling the sequential dependence among audience multi-step conversions","Multi-step-Conv",2021,"Meituan","KDD","cvr",["mtl"],"Multi-step conversion chains in targeted display ads."),
 ("mal","multi-attribution learning","MAL",2025,"Alibaba","CIKM","cvr",["mtl"],"Multi-attribution learning for better CVR prediction."),
 ("eslm","unbias conversion rate prediction in full stages","ESLM",2023,"Alibaba","arXiv","cvr",["mtl","debias"],"Unbiased CVR across all stages of the recommender."),
 ("hapfd","hardness-aware privileged features distillation","HA-PFD",2025,"Bytedance","KDD","cvr",["distill"],"Privileged-feature distillation for CVR at ByteDance."),
 ("couponcvr","on the practice of scaling search conversion rate prediction","CVR-Scaling",2026,"Coupon","arXiv","cvr",["scaling"],"Scaling practice for search-ads conversion-rate prediction."),
 # ---- delayed feedback ----
 ("dfm","modeling delayed feedback in display advertising","DFM",2014,"Criteo","KDD","delayed",[],"The delayed-feedback model: exponential delay + importance weighting."),
 ("nodef","nonparametric delayed feedback model","NoDeF",2018,None,"arXiv","delayed",[],"Nonparametric delay distribution for CVR."),
 ("twitterdf","addressing delayed feedback for continuous training","TW-DF",2019,"Twitter","RecSys","delayed",[],"Importance-weighted streaming CVR under delayed feedback."),
 ("tsdl","attention-based model for conversion rate prediction with delayed feedback","TS-DL",2020,"JD","IJCAI","delayed",[],"Post-click calibration + attention for delayed conversions."),
 ("fsiw","feedback shift correction","FSIW",2020,None,"WWW","delayed",[],"Feedback-shift-corrected CVR under delayed labels."),
 ("esdfm","capturing delayed feedback in conversion rate prediction","ES-DFM",2021,"Alibaba","AAAI","delayed",["mtl"],"Elapsed-time sampling for delayed feedback in the entire space."),
 ("esdf","delayed feedback modeling for the entire space","ESDF",2021,"Alibaba","AAAI","delayed",["mtl"],"Entire-space DFM variant for CVR."),
 ("defer","real negatives matter","Defer",2021,"Alibaba","arXiv","delayed",[],"Real negatives for delayed-feedback modeling in streaming CTR."),
 ("defuse","asymptotically unbiased estimation","DEFER",2022,"Alibaba","WWW","delayed",[],"Label correction for asymptotically unbiased delayed-feedback CVR."),
 ("nbdfm","delayed feedback model with negative binomial regression","NB-DFM",2020,None,"ADKDD","delayed",[],"Negative-binomial delay for multiple conversions."),
 ("manyconv","handling many conversions per click","Many-Conv",2021,"Google","arXiv","delayed",[],"Delayed feedback with many conversions per click."),
 # ---- calibration ----
 ("scalecalib","scale calibration of deep ranking models","Scale-Calib",2022,"Google","KDD","calibration",[],"Production calibration of deep ads ranking models."),
 ("rankcalib","joint optimization of ranking and calibration","Rank-Calib",2023,"Alibaba","KDD","calibration",[],"Contextual hybrid model jointly optimizing ranking loss and calibration."),
 # ---- relevance ----
 ("masm","learning a product relevance model from click-through","MASM",2021,"Alibaba","WWW","relevance",[],"Product relevance learned from click-through data in e-commerce search."),
 ("hcmrm","high-consistency multimodal relevance model","HCMRM",2025,"Kuaishou","arXiv","relevance",["mm"],"High-consistency multimodal relevance for search ads."),
 # ---- generative / unified ----
 ("gpr","gpr - towards a generative pre-trained one-model","GPR",2025,"Tencent","arXiv","generative",["genllm"],"Generative pre-trained one-model paradigm for large-scale advertising recommendation."),
 ("unirom","one model to rank them all","UniROM",2025,"Meituan","arXiv","generative",["genllm"],"End-to-end unified learning across the online advertising pipeline."),
 ("llmdistill","using cross-encoders to distill from llm signals","LLMDistill4Ads",2025,"eBay","arXiv","generative",["genllm","distill"],"Cross-encoder distillation of LLM signals for advertiser keyphrase recommendations."),
 # ---- multimodal ----
 ("imagectr","image matters - visually modeling user behaviors","Image-CTR",2018,"Alibaba","CIKM","ctr",["mm","seq"],"Visual behavior modeling via model server for display-ads CTR."),
 ("taobaomm","enhancing taobao display advertising with multimodal","Taobao-MM",2024,"Alibaba","CIKM","ctr",["mm"],"Multimodal representations in Taobao display advertising."),
]

# ---------------------------------------------------------------- curated lineage (source -> target, label)
LINEAGE = [
 ("lrftrl","fblessons","FTRL & sparse LR -> GBDT/LR feature systems"),
 ("fblessons","twitterctr","ads CTR feature practice"),
 ("lrdisplay","fblessons","layered LR response models"),
 ("lrftrl","dcn","Google ads CTR: FTRL -> cross network"),
 ("deepintent","din","attention on ads -> attention on behaviors"),
 ("ffm","deepfm","FM -> FM-based DNN"),
 ("deepfm","fgcnn","CTR feature engineering -> auto feature generation"),
 ("dcn","gdcn","cross network -> improved cross network"),
 ("dcn","memonet","cross features -> memorized cross representations"),
 ("fibinet","gatenet","SENet -> feature gating"),
 ("fibinet","fibinet2","bilinear -> low-rank bilinear"),
 ("gatenet","masknet","gating -> instance-wise masks"),
 ("din","dien","interest activation -> interest evolution"),
 ("din","dsin","interests -> session interests"),
 ("din","dhan","attention -> hierarchical attention"),
 ("din","dstn","behavior -> + context/auxiliary ads"),
 ("din","mimn","long behaviors in production"),
 ("din","dihn","interest highlighting for trigger ads"),
 ("mimn","sim","memory server -> two-stage lifelong search"),
 ("sim","eta","hard search -> SimHash retrieval"),
 ("ubr4ctr","eta","behavior retrieval -> efficient hashing"),
 ("sim","sdim","long-term modeling -> hash sampling"),
 ("sim","twin","two-stage -> end-to-end twin towers"),
 ("twin","twin2","scaling to ultra-long sequences"),
 ("mimn","lcn","lifelong -> cross-domain lifelong"),
 ("sim","lrea","long-seq attention -> low-rank attention"),
 ("sim","bahe","long behaviors -> LLM-encoded behaviors"),
 ("esmm","esm2","post-click behavior decomposition"),
 ("esmm","causaldebias","post-click CVR debiasing"),
 ("esmm","hm3","entire space -> micro/macro multi-task"),
 ("esmm","esdfm","entire space + delayed feedback"),
 ("esmm","esdf","entire-space DFM"),
 ("esmm","eslm","unbiased CVR across full stages"),
 ("esm2","meituanconv","decomposition -> multi-step conversions"),
 ("esmm","mal","post-click CVR -> multi-attribution"),
 ("dfm","nodef","parametric -> nonparametric delay"),
 ("dfm","twitterdf","importance weighting for streaming"),
 ("dfm","tsdl","delay model -> post-click calibration"),
 ("dfm","fsiw","feedback shift correction"),
 ("dfm","esdfm","delay + entire space"),
 ("dfm","esdf","delay + entire space"),
 ("dfm","defer","importance weighting -> real negatives"),
 ("dfm","defuse","delay modeling -> label correction"),
 ("dfm","nbdfm","single -> multiple conversions"),
 ("dfm","manyconv","multi-conversion delay modeling"),
 ("mobius","rare","query-ad matching -> LLM commercial intent"),
 ("mobius","gr4ad","ads retrieval -> generative ads recommendation"),
 ("gpr","gr4ad","generative one-model ads paradigm"),
 ("minet","star","cross-domain -> multi-domain star topology"),
 ("star","adasparse","multi-domain -> adaptive sparsity"),
 ("star","apg","-> scenario-conditioned parameters"),
 ("star","mmn","-> masked multi-domain MoE"),
 ("star","mlora","-> scenario LoRA adapters"),
 ("star","hc2","-> scenario contrastive alignment"),
 ("minet","rec4ad","cross-domain -> rec-to-ads transfer"),
 ("deepmcp","copr","matching/ranking consistency -> cascade consistency"),
 ("fblessons","scalecalib","a decade of CTR calibration practice"),
 ("scalecalib","rankcalib","calibration + ranking consistency"),
 ("fblessons","factory","a decade of ads ML engineering"),
 ("dhen","interformer","sparse ensemble -> heterogeneous interaction"),
 ("dhen","lattice","ensemble stacking -> lattice model space"),
 ("dhen","rankup","-> high-rank ensemble representations"),
 ("dhen","exfm","sparse ensembles -> trillion-param foundation"),
 ("exfm","llatte","foundation serving -> scaling laws"),
 ("sum","llatte","user representations -> multi-stage seq scaling"),
 ("fat","est","transformer CTR -> unified scaling laws"),
 ("masm","hcmrm","relevance -> multimodal relevance"),
 ("imagectr","taobaomm","visual behaviors -> multimodal display ads"),
 ("dcin","unirom","Meituan CTR -> unified ads ranking"),
 ("srp4ctr","unirom","sequential pretraining -> end-to-end ROM"),
]
SURVEY_COVERS = [("dltr", k) for k in ("din","esmm","dfm","mobius","lattice")]

# ---------------------------------------------------------------- assemble nodes
def find_entry(substrs, alt=()):
    keys = list(alt) + [substrs]
    for k in keys:
        for e in unique.values():
            if k in norm(e["title"]):
                return e
    return None

nodes, edges = [], []
node_ids = set()
stage_members = {s: 0 for s in STAGES}

def add_node(nid, ntype, label, **kw):
    if nid in node_ids:
        return
    node_ids.add(nid)
    n = {"id": nid, "type": ntype, "label": label}
    n.update(kw)
    nodes.append(n)

paper_meta = {}
for (key, match, tag, year, company, venue, stage, themes, note) in PAPERS:
    e = find_entry(match)
    if e is None:
        print(f"!! no README match for {key}: {match}")
        continue
    stars = stars_of(e["title"])
    add_node(key, "paper", tag or e["title"][:40],
             title=re.sub(r"\s+", " ", e["title"]).strip(),
             year=year, company=company, venue=venue, stage=stage,
             themes=themes, stars=stars, note=note, url=e["url"],
             listed=len(e["sections"]))
    paper_meta[key] = dict(company=company, venue=venue, stage=stage, themes=themes)
    stage_members[stage] += 1
    # stage edge
    edges.append({"s": key, "t": "stage:"+stage, "r": "stage"})
    # theme edges
    for th in themes:
        edges.append({"s": key, "t": "theme:"+th, "r": "theme"})
    # company edge
    if company:
        cid = "co:" + COMPANIES[company]
        edges.append({"s": key, "t": cid, "r": "company"})
    # venue edge
    if venue:
        v = VENUE_FIX.get(venue, venue)
        edges.append({"s": key, "t": "venue:" + v, "r": "venue"})

# hubs
for sid, (label, color, desc) in STAGES.items():
    add_node("stage:"+sid, "stage", label, color=color, desc=desc, count=stage_members[sid])
for tid, (label, desc) in THEMES.items():
    add_node("theme:"+tid, "theme", label, desc=desc)
for name, cid in COMPANIES.items():
    add_node("co:" + cid, "company", COMPANY_LABEL.get(cid, name))
for v in sorted(VENUES):
    add_node("venue:" + v, "venue", v)

# lineage edges
for s, t, label in LINEAGE:
    if s not in paper_meta or t not in paper_meta:
        print(f"!! lineage refs unknown paper: {s}->{t}")
        continue
    edges.append({"s": s, "t": t, "r": "lineage", "label": label})
for s, t in SURVEY_COVERS:
    edges.append({"s": s, "t": t, "r": "covers", "label": "survey covers"})

kg = {
    "meta": {
        "name": "Ads Papers Knowledge Graph",
        "source": "Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising",
        "generated": "2026-09-19",
        "nodeCount": len(nodes), "edgeCount": len(edges),
    },
    "nodes": nodes, "edges": edges,
}
with open(os.path.join(HERE, "knowledge_graph.json"), "w", encoding="utf-8") as f:
    json.dump(kg, f, ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- self-contained HTML viewer
tpl_path = os.path.join(HERE, "template.html")
if os.path.exists(tpl_path):
    tpl = open(tpl_path, encoding="utf-8").read()
    data_js = json.dumps(kg, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("__KG_DATA__", data_js)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html written:", len(html) // 1024, "KB")

# ---------------------------------------------------------------- stats
from collections import Counter
print("papers:", sum(1 for n in nodes if n["type"] == "paper"))
print("by stage:", {STAGES[k][0]: v for k, v in stage_members.items() if v})
print("by company:", Counter(n["company"] for n in nodes if n["type"] == "paper" and n["company"]))
print("nodes:", len(nodes), "edges:", len(edges),
      "lineage:", sum(1 for e in edges if e["r"] == "lineage"))
