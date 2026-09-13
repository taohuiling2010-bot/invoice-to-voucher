# 供应商→借方科目映射，与 data/映射表.xlsx 保持一致
MAPPING = {
    "上海远景办公设备有限公司": "管理费用—办公费",
    "苏州卓信家具有限公司":     "管理费用—办公费",
    "深圳恒瑞办公耗材有限公司": "管理费用—办公费",
    "宁波启航数码设备有限公司": "管理费用—办公费",
    "北京华创办公设备有限公司": "管理费用—办公费",
    "天津卓信办公科技有限公司": "管理费用—办公费",
    "上海启越办公设备有限公司": "管理费用—办公费",
    "苏州博远电子有限公司":     "管理费用—办公费",
    "北京恒信办公设备有限公司": "管理费用—办公费",
    "北京筑诚工程服务有限公司": "长期待摊费用—装修费",
    "天津安厦建筑工程有限公司": "长期待摊费用—装修费",
    "广州云衡信息技术有限公司": "管理费用—服务费",
    "杭州智维咨询科技有限公司": "管理费用—服务费",
    "上海智创信息技术有限公司": "管理费用—服务费",
}
VAT_INPUT = "应交税费—应交增值税（进项税额）"
PAYABLE   = "应付账款"

async def main(args: Args) -> Output:
    p = args.params
    status = p.get("status") or ""
    reason = p.get("reason") or ""
    seller = (p.get("seller") or "").strip()

    # 校验已异常：原样放行，不生成分录
    if status != "通过":
        return {"status": status, "reason": reason,
                "debit_account": "", "voucher_text": ""}

    debit = MAPPING.get(seller)
    if not debit:
        return {"status": "异常", "reason": "供应商未映射",
                "debit_account": "", "voucher_text": ""}

    amount = float(p.get("amount") or 0)
    tax    = float(p.get("tax") or 0)
    total  = float(p.get("total") or 0)
    summary = f"{p.get('issue_date','')} {seller} 发票{p.get('invoice_code','')}-{p.get('invoice_no','')}"

    lines = [
        f"摘要：{summary}",
        f"借：{debit}  {amount:,.2f}",
        f"借：{VAT_INPUT}  {tax:,.2f}",
        f"    贷：{PAYABLE}—{seller}  {total:,.2f}",
    ]
    ret: Output = {"status": "通过", "reason": "",
                   "debit_account": debit, "voucher_text": "\n".join(lines)}
    return ret