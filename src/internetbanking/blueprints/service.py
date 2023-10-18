from db import session
from models import Transaction
#scritp untuk melakukan pengecekkan dormant

query = """
UPDATE tb_account
SET is_active = False
WHERE id_account NOT IN (
    SELECT
    tb_account.id_account
FROM
    tb_account 
LEFT JOIN 
	tb_user AS u ON u.id_user = tb_account.id_user 
LEFT JOIN
    tb_transaction AS from_transaction ON tb_account.id_account = from_transaction.from_account_id
LEFT JOIN
    tb_transaction AS to_transaction ON tb_account.id_account = to_transaction.to_account_id
WHERE
	u."is_admin" IS FALSE AND 
    (from_transaction.created_at >= NOW() - INTERVAL '3 months')
    or (to_transaction.created_at >= NOW() - INTERVAL '3 months')
GROUP BY tb_account.id_account
);
"""

accounts = session.execute(query)
for account in accounts:
    account.is_active = False
session.commit()