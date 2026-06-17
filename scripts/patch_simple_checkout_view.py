#!/usr/bin/env python3
"""Patch warunglakku.simple_checkout view (id 3235) to fix broken
`checkout.get('street', '')` expression.

The expression crashes when `checkout` is a res.partner record (editing
existing address via /shop/address?partner_id=N). Replaces with
`checkout['street']` which works for both dict and res.partner record.
"""
import sys
sys.path.insert(0, "/home/z/my-project/scripts")
from portainer_psql import psql

SEARCH = "checkout.get('street', '') if 'street' in checkout else ''"
REPLACE = "checkout['street'] if 'street' in checkout else ''"

# Use dollar-quoting to avoid single-quote escaping nightmares.
# Dollar-quoting tag must not appear in the body.
SQL_UPDATE = f"""
UPDATE ir_ui_view
SET arch_db = (
    SELECT jsonb_object_agg(lang, REPLACE(content::text,
        $token${SEARCH}$token$,
        $token${REPLACE}$token$)::jsonb)
    FROM jsonb_each(arch_db) AS t(lang, content)
)
WHERE id = 3235
  AND arch_db::text LIKE $token$%checkout.get('street%$token$;
"""

SQL_CHECK = """
SELECT id, key,
    (arch_db::text LIKE '%checkout.get(%') AS has_broken_get,
    (arch_db::text LIKE $token$%checkout[''street'']%$token$) AS has_fixed_indexing
FROM ir_ui_view WHERE id = 3235;
"""


def main():
    print("=== BEFORE: state of view 3235 ===")
    code, out, err = psql(SQL_CHECK)
    print(out)
    if err.strip():
        print("STDERR:", err)
        if code != 0:
            sys.exit(1)

    print("\n=== APPLYING PATCH ===")
    code, out, err = psql(SQL_UPDATE)
    print(out)
    if err.strip():
        print("STDERR:", err)
        if code != 0:
            sys.exit(1)

    print("\n=== AFTER: state of view 3235 ===")
    code, out, err = psql(SQL_CHECK)
    print(out)
    if err.strip():
        print("STDERR:", err)


if __name__ == "__main__":
    main()
