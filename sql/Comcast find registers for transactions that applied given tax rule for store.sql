-- find tax percentage for all rules for store
SELECT tax_loc.TAX_LOC_ID, NAME, tax_rule.PERCENTAGE, tax_rule.EFFECTIVE_DATETIME, tax_rule.EXPR_DATETIME
FROM TAX_TAX_RATE_RULE tax_rule, TAX_TAX_LOC tax_loc, tax_rtl_loc_tax_mapping tax_rtl_map
WHERE tax_rule.ORGANIZATION_ID = tax_loc.ORGANIZATION_ID
AND tax_loc.ORGANIZATION_ID = tax_rtl_map.ORGANIZATION_ID
AND tax_rule.TAX_LOC_ID = tax_loc.TAX_LOC_ID
AND tax_rtl_map.TAX_LOC_ID = tax_loc.TAX_LOC_ID
AND tax_rtl_map.RTL_LOC_ID = '800'

-- find workstation and lineitem with item of given tax group at given retail location
-- todo find if wkstn is primary or not
SELECT dev_reg.PRIMARY_REGISTER_FLAG, dev_reg.WKSTN_ID, (li.GROSS_AMT - li.NET_AMT) AS tax 
FROM trl_sale_lineitm li, TAX_TAX_GROUP tax_grp, CTL_DEVICE_REGISTRATION dev_reg
WHERE li.TAX_GROUP_ID = '3'
AND li.RTL_LOC_ID = '800'
AND (li.GROSS_AMT - li.NET_AMT) > 0	-- only LIs with tax amount
AND dev_reg.ORGANIZATION_ID = li.ORGANIZATION_ID
AND dev_reg.WKSTN_ID = li.WKSTN_ID
AND dev_reg.RTL_LOC_ID = li.RTL_LOC_ID

-- same as above add the tax rule information

-- any register that has performed a transaction with a line item that a given tax rule was applied to including whether the register is a lead or not
SELECT DISTINCT dev_reg.PRIMARY_REGISTER_FLAG, dev_reg.WKSTN_ID
FROM trl_sale_lineitm li, TAX_TAX_GROUP tax_grp, CTL_DEVICE_REGISTRATION dev_reg, TAX_TAX_RATE_RULE tax_rule, tax_rtl_loc_tax_mapping tax_rtl_map
-- join tax_rtl_map on LI to find tax_loc_id for tax_rule
WHERE tax_rtl_map.ORGANIZATION_ID = li.ORGANIZATION_ID
AND tax_rtl_map.RTL_LOC_ID = li.RTL_LOC_ID
-- join LI and Rule on PK
AND tax_rule.ORGANIZATION_ID = li.ORGANIZATION_ID
AND tax_rule.TAX_GROUP_ID = li.TAX_GROUP_ID
-- get tax loc id from tax_rtl_map
AND tax_rule.TAX_LOC_ID = tax_rtl_map.TAX_LOC_ID
-- specify the rest of the tax rule primary key
AND tax_rule.TAX_RULE_SEQ_NBR = '1'
AND tax_rule.tax_rate_rule_seq = '1'
-- specify store
AND li.RTL_LOC_ID = '800'
-- limit to LIs with tax
AND (li.GROSS_AMT - li.NET_AMT) > 0
-- join LI and register
AND dev_reg.ORGANIZATION_ID = li.ORGANIZATION_ID
AND dev_reg.WKSTN_ID = li.WKSTN_ID
AND dev_reg.RTL_LOC_ID = li.RTL_LOC_ID

-- any register that has NOT performed a transaction with a line item that a given tax rule was applied to including whether the register is a lead or not
SELECT wkstn.WKSTN_ID, dev_reg.PRIMARY_REGISTER_FLAG 
FROM LOC_WKSTN wkstn, CTL_DEVICE_REGISTRATION dev_reg
WHERE wkstn.WKSTN_ID NOT IN 
	(SELECT DISTINCT li.WKSTN_ID
	FROM trl_sale_lineitm li, TAX_TAX_GROUP tax_grp, CTL_DEVICE_REGISTRATION dev_reg, TAX_TAX_RATE_RULE tax_rule, tax_rtl_loc_tax_mapping tax_rtl_map
	-- join tax_rtl_map on LI to find tax_loc_id for tax_rule
	WHERE tax_rtl_map.ORGANIZATION_ID = li.ORGANIZATION_ID
	AND tax_rtl_map.RTL_LOC_ID = li.RTL_LOC_ID
	-- join LI and Rule on PK
	AND tax_rule.ORGANIZATION_ID = li.ORGANIZATION_ID
	AND tax_rule.TAX_GROUP_ID = li.TAX_GROUP_ID
	-- get tax loc id from tax_rtl_map
	AND tax_rule.TAX_LOC_ID = tax_rtl_map.TAX_LOC_ID
	-- specify the rest of the tax rule primary key
	AND tax_rule.TAX_RULE_SEQ_NBR = '1'
	AND tax_rule.tax_rate_rule_seq = '1'
	-- specify store
	AND li.RTL_LOC_ID = '800'
	-- limit to LIs with tax
	AND (li.GROSS_AMT - li.NET_AMT) > 0
	-- join LI and register
	AND dev_reg.ORGANIZATION_ID = li.ORGANIZATION_ID
	AND dev_reg.WKSTN_ID = li.WKSTN_ID
	AND dev_reg.RTL_LOC_ID = li.RTL_LOC_ID)


SELECT * FROM TAX_TAX_LOC

SELECT * FROM TAX_TAX_RATE_RULE

SELECT * FROM tax_rtl_loc_tax_mapping

SELECT * FROM TAX_TAX_GROUP

SELECT * FROM CTL_DEVICE_REGISTRATION

SELECT * FROM LOC_WKSTN

select distinct TO_CHAR(t.trans_date, 'DD/MM/YYYY'), r.AREA, t.*, l.item_id
from trn_trans t, TRL_SALE_LINEITM l, loc_rtl_loc r, tax_tax_rate_rule tt, tax_rtl_loc_tax_mapping tr, dtv.trl_sale_lineitm_org tslo
where TRANS_TYPCODE='RETAIL_SALE'
and TRANS_STATCODE='COMPLETE' 
and t.RTL_LOC_ID = r.RTL_LOC_ID 
AND t.WKSTN_ID = l.WKSTN_ID 
and t.BUSINESS_DATE = l.BUSINESS_DATE 
and t.RTL_LOC_ID = l.RTL_LOC_ID
and t.ORGANIZATION_ID = l.ORGANIZATION_ID 
and t.trans_seq =l.trans_seq
and l.tax_group_id =1
and t.total >0
and t.taxtotal=0
and tt.tax_loc_id =tr.tax_loc_id 
and tr.rtl_loc_id =t.rtl_loc_id 
and tslo.rtl_loc_id =t.rtl_loc_id
and tslo.wkstn_id =t.wkstn_id
and tslo.return_flag =0
and tt.tax_group_id =1 and
r.rtl_loc_id not in 
	(select distinct RTL_LOC_ID 
	from loc_rtl_loc 
	where length(RTL_LOC_ID)>3 
	and telephone4 is not null  
	AND TO_DATE(TELEPHONE4,'MM/DD/YY') <= SYSDATE 
	and RTL_LOC_ID not in (3112,2902,1406,1407,2102,777,3350,5001,778,2026,1606) 
	and state in ('DE','NH','OR'))
and t.create_date between sysdate-1/24 and sysdate;
