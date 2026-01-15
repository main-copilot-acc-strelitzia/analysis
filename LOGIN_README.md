LOGIN CREDENTIALS
=================

Username: leblanc
Password: the pale woman

Note: These credentials are NOT hardcoded in HTML (to prevent F12 visibility).
They are validated server-side in ui/webapp.py.

PAGES & CSS STATUS
==================

✓ /login      - Uses /static/css/styles.css
✓ /           - Uses /static/css/styles.css (main dashboard)
✓ /login (error) - Uses /static/css/styles.css (styled error page)

DEBUGGING LOGIN ISSUES
======================

If login fails (401 Unauthorized):

1. Check browser console (F12) for JavaScript errors
2. Check server logs for login attempt details (now includes username/password length)
3. Ensure credentials are typed exactly:
   - Username: "leblanc" (lowercase)
   - Password: "the pale woman" (with space, lowercase)

4. Try the test_login.py script:
   python test_login.py

CHART.JS FILES
==============

All 15 MetaTrader Chart.js files are available in the dropdown:
- 6mRdyiCx.js
- 8UKJi1cj.js
- 78Fx-YMV.js
- B6FSvflP.js
- BAH8vq5n.js
- BOqoXv1X.js
- BPQc8Glp.js
- Bp5cWvCe.js
- BtviGlP5.js
- C5qKhnQP.js
- CQ67ee1G.js
- DEvOfyNb.js
- DiXDOeOw.js
- HcGwWu0z.js
- Iah0KJMP.js

Plus standard Chart.js fallbacks in /static/js/
