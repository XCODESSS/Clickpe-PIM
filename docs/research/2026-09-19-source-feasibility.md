# Planning reconnaissance — 2026-09-19

These are read-only feasibility checks from the planning session. No production scraper, database, gold labels, accuracy result or monitoring history exists yet. Recheck these URLs and contracts when implementing; web content can change.

## Local starting point

`D:\Clickpe-PIM` was empty and was not a Git repository. No `AGENTS.md` existed in the workspace or at `D:\AGENTS.md`. Python 3.12.6, Git 2.47.1.windows.1 and `uv` were available. Existing global package versions included requests 2.32.5, BeautifulSoup 4.12.3, Pydantic 2.12.5, pandas 2.3.3, PyArrow 20.0.0, Streamlit 1.52.1, Plotly 6.9.0, RapidFuzz 3.14.3 and pytest 8.4.2. These observations are not a tested project dependency lock.

## ClickPe public collection route

- [Homepage](https://clickpe.ai/) links to `/product?category=Personal+Loans` and `/product?category=Business+Loans`. Loan against property links to a Google form; do not submit it.
- [robots.txt](https://clickpe.ai/robots.txt) returned HTTP 200 with a public allow rule and a sitemap. Inspect again per collection run.
- [Sitemap](https://clickpe.ai/sitemap.xml) includes `/products`, while the homepage uses singular `/product`. Do not assume sitemap paths are the actual catalogue contract.
- An ordinary HTTP GET of `/product?category=Personal+Loans` returned a JavaScript shell with no product links/text. The public script `/_next/static/chunks/148-a0f5ecd42e7f0d22.js` exposed `getLandingProducts()`, base `/api/proxy`, and GET `/products?channel=landing`. Chunk hashes are discovery evidence, never stable configuration.
- [Public catalogue feed](https://clickpe.ai/api/proxy/products?channel=landing) returned HTTP 200 and JSON keys `status`, `message`, `error`, `response`; status was `Success`, and `response` was a list. A requests GET succeeded even though the web reading tool could not render this URL.
- The observed feed had **67 records**: Personal Loan 31, Business Loan 3, Savings Account 6, Credit Card 19, Demat Account 5, Loan Against Property 1, EMI Conversion 1, Loan Against Credit Card 1. There was no separate credit-line category in that response. These are feed counts, not a completed displayed-catalogue audit.
- The feed supplies `id`, `name`, `category`, `lender`, `status`, `ranking`, `content.headline` and `content.keyBenefits`. It also includes application/form configuration. Extract public display content first; field validation bounds, calculator inputs, ranking, payouts and application defaults are not automatically product terms.
- The catalogue client builds cards from the feed and opens a detail modal. Do not invent one public detail URL per product. Preserve the catalogue URL plus native product ID and a JSON pointer as the evidence locator.
- The browser preview opened the category page, but its snapshot call failed. Visual equivalence of the feed to all rendered cards remains an implementation acceptance check.

## Observations that shape the tests

1. `prefr_pl` advertises a maximum of INR 500,000 in its catalogue headline. ClickPe's [partner page](https://clickpe.ai/partners) has a lower upper bound in its Prefr/Hero disclosure. Programme applicability is unconfirmed; seed this as an internal ambiguity requiring review, not a proven error.
2. `muthoot_emi_bl` and `muthoot_daily_bl` are separate native IDs. Preserve them even if an alias matches their shared brand. Their raw `lender` string differs from the FinCorp name in the partner disclosure; do not silently equate Finance and FinCorp.
3. `vivifi_pl` is categorized as a personal loan, but its returned content refers to a savings account and deposit interest. A category/content check should quarantine loan-rate extraction and retain the evidence.
4. Some short-term loans have a numeric starting rate with no stated period. Store unknown period; do not infer monthly or annual from neighbouring products.
5. [InCred's official personal-loan page](https://incred.com/personal-loan/) contains product terms, APR, eligibility and documentation alongside an EMI calculator and a worked example. Exclude calculator controls and representative examples from general offer assertions.

## Official source candidates, not approved programme mappings

| Product or entity | URL | Use and open question |
|---|---|---|
| ClickPe partner relationships | https://clickpe.ai/partners | Internal programme/entity claims |
| ClickPe support disclosures | https://clickpe.ai/support | Internal role/registration claims |
| Prefr personal loans | https://prefr.com/personal-loan | Official brand product page; identify programme and lender |
| Prefr relationships | https://prefr.com/lending-partners | Multiple lenders; no automatic one-to-one Hero mapping |
| InCred personal loan | https://incred.com/personal-loan/ | Official comparable product candidate; distinguish calculator/example blocks |
| FlexiLoans business loan | https://flexiloans.com/business-loan | Official product candidate; establish applicability to the ClickPe channel |
| Muthoot FinCorp | https://www.muthootfincorp.com/ | Linked from ClickPe disclosure; programme-specific source remains to be researched |
| Vivifi | https://www.vivifin.com/ | Linked from ClickPe disclosure; programme-specific source remains to be researched |

The broad brief mentioned Poonawalla/Hero offerings. Neither name appeared as a separate product in the inspected 35 Personal Loan/Business Loan/LAP records. Do not populate them solely from the brief. A provider can still appear in a verified entity relationship without a separate catalogue offering.

## Documentation checked for the implementation plan

- [Python 3.12 SQLite transactions and backup API](https://docs.python.org/3.12/library/sqlite3.html).
- [Requests: timeouts and HTTP/JSON status handling](https://requests.readthedocs.io/en/latest/user/quickstart/).
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/).
- [pandas Parquet export](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html).
- [pytest temporary directories](https://docs.pytest.org/en/stable/how-to/tmp_path.html).
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest): initialize from the entrypoint, switch pages, then explicitly call `run()`.

The source inspection establishes feasibility and test cases. The implementation must save frozen bytes and hashes before making reportable extraction or comparison claims.

