# Import Purchase Tracking — Odoo 19

## Features
- BOE register with one BOE linked to multiple purchase orders.
- Different PO suppliers are retained from each Purchase Order.
- Vendor bills and vendor credit notes can reference a BOE.
- One vendor bill can be allocated across multiple POs using multiple allocation records.
- Separate bill supplier and PO supplier fields.
- Manual charge allocation in company currency.
- Posted vendor bills are included in BOE totals; draft/cancelled bills are excluded.
- Vendor credit notes reduce the relevant charge category totals.
- No journal entries are created and no accounting amounts are modified.

## Installation
1. Copy `import_purchase_tracking` into a custom addons directory in your Odoo.sh repository.
2. Commit and push to your Odoo.sh staging branch.
3. Update the Apps list in the staging database.
4. Install **Import Purchase Tracking**.
5. Create a BOE in Import Purchase > BOE Register.
6. Add all relevant Purchase Orders in the Purchase Orders tab.
7. Open each vendor bill and select its Import BOE.
8. In the BOE's Charge Allocations tab, create one allocation per bill expense line and PO.
9. Enter the amount allocated to that PO in company currency.

## Important operating rules
- The selected bill line must be a product/expense line posted to an expense account.
- The bill must reference the same BOE as the allocation.
- The PO must first be linked to that BOE.
- Total allocations against a bill line cannot exceed that line's company-currency balance.
- Use separate allocation rows when one bill line is shared across multiple POs.
- If a vendor bill line is in foreign currency, allocate using the company-currency amount shown by Odoo (`balance`).
- Configure your account mapping operationally by selecting the correct charge type on each allocation.

## Before production
This is a starter module and must be tested against your exact Odoo.sh 19 Enterprise build and custom modules on a staging database. In particular:
- Confirm the `account.view_move_form` external ID and the invoice form xpath against your installed build.
- Test bill creation, posting, reversal, credit notes, multi-company access and foreign currencies.
- Review security groups and record rules for your company's accounting policy.
- If you need a strict rule that all posted allocations must reconcile to the entire expense line, add a finalization/check workflow; this starter allows partial allocations.
