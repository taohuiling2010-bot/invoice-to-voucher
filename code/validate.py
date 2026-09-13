import json

VALID_RATES = {13, 9, 6, 5, 3, 1, 0}
TOL = 0.01  # 金额比对容差，票面四舍五入到分

async def main(args: Args) -> Output:
    p = args.params
    raw = (p.get("llm_output") or "").strip()
    # 去掉模型可能带的 ```json 围栏
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[4:] if raw.lower().startswith("json") else raw
    try:
        d = json.loads(raw)
    except Exception:
        return {"status": "异常", "reason": "提取结果不是合法JSON",
                "invoice_code": "", "invoice_no": "", "issue_date": "",
                "seller": "", "seller_tax_id": "", "buyer": "", "key": "",
                "amount": 0, "tax_rate": 0, "tax": 0, "total": 0}

    def num(x):
        try:
            return float(str(x).replace(",", "").replace("¥", "").replace("%", ""))
        except Exception:
            return None

    amount = num(d.get("金额"))
    rate   = num(d.get("税率"))
    tax    = num(d.get("税额"))
    total  = num(d.get("价税合计"))
    code   = str(d.get("发票代码") or "")
    no     = str(d.get("发票号码") or "")
    key    = f"{code}-{no}"

    reasons = []
    if None in (amount, rate, tax, total) or not code or not no:
        reasons.append("字段缺失")
    else:
        if rate not in VALID_RATES:
            reasons.append("税率非法")
        elif abs(amount * rate / 100 - tax) > TOL:
            reasons.append("税额不符")
        if abs(amount + tax - total) > TOL:
            reasons.append("价税合计不符")
        booked = {k.strip() for k in (p.get("booked_keys") or "").split(",") if k.strip()}
        if key in booked:
            reasons.append("号码重复")

    ret: Output = {
        "status": "异常" if reasons else "通过",
        "reason": "；".join(reasons),
        "invoice_code": code, "invoice_no": no,
        "issue_date": str(d.get("开票日期") or ""),
        "seller": str(d.get("销方名称") or ""),
        "seller_tax_id": str(d.get("销方税号") or ""),
        "buyer": str(d.get("购方名称") or ""),
        "key": key,
        "amount": amount or 0, "tax_rate": rate or 0,
        "tax": tax or 0, "total": total or 0,
    }
    return ret