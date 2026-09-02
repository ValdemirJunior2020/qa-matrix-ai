# QA Matrix AI build report

## Uploaded Matrix inspection

- Workbook file: `new matrix-06_22_26(10).xlsx`
- Sheets: `Voice Matrix`, `Ticket Matrix`, `Items to note`
- Parsed logical Matrix records: 99
- Explicit Critical records detected: 0
- Explicit scoring records detected: 0
- Initial active Matrix SHA256: `8455771ff1f239fca1c87debef168f724986e588fafe669eab97f7e1b466a041`

The parser is adaptive and retains workbook/sheet/category/rule/action fields, cell range, source row, comments, formula cells and basic style hints. It does not assume a fixed QA schema.

## Verification completed

- Python source compilation passed.
- Parser tests passed against the included real workbook.
- Password hashing/verification test passed.
- Guardrail test confirms missing Matrix scores are not invented.
- Guardrail test confirms a Critical label alone cannot automatically zero a score unless the Matrix explicitly defines that behavior.

Frontend dependencies are intentionally not included in the ZIP. Run `npm install` in `frontend` (or let Netlify install dependencies during deployment). The build environment used to package this artifact could not complete the external npm download before its network timeout, so the frontend production build should be run on your Windows machine/Netlify as documented.
