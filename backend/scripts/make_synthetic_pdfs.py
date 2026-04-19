"""
Generate 7 synthetic PDFs for the FinGuard RAG corpus.
Run from the finguard-rag/backend directory:
    python scripts/make_synthetic_pdfs.py
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"

STYLES = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle("title", parent=STYLES["Title"], fontSize=16, spaceAfter=20)
H1_STYLE = ParagraphStyle("h1", parent=STYLES["Heading1"], fontSize=13, spaceAfter=10, spaceBefore=14)
H2_STYLE = ParagraphStyle("h2", parent=STYLES["Heading2"], fontSize=11, spaceAfter=8, spaceBefore=10)
BODY_STYLE = ParagraphStyle("body", parent=STYLES["Normal"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
SMALL_STYLE = ParagraphStyle("small", parent=STYLES["Normal"], fontSize=8, leading=11, spaceAfter=4)


def _page_num_canvas(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(A4[0] - 2 * cm, 1.5 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _build_pdf(filename: str, elements: list) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                            topMargin=2.5 * cm, bottomMargin=2.5 * cm)
    doc.build(elements, onFirstPage=_page_num_canvas, onLaterPages=_page_num_canvas)
    print(f"  Created: {path}")


def _p(text: str, style=None) -> Paragraph:
    return Paragraph(text, style or BODY_STYLE)


def _sp(n: int = 1) -> Spacer:
    return Spacer(1, n * 0.4 * cm)


# ── 1. RBI Loans and Advances ────────────────────────────────────────────────

def make_rbi_loans():
    e = [
        _p("Reserve Bank of India", TITLE_STYLE),
        _p("Master Circular — Loans and Advances: Statutory and Other Restrictions", TITLE_STYLE),
        _p("Ref: RBI/2024-25/LC/001 | Dated: April 1, 2024", SMALL_STYLE),
        _sp(2),
        _p("Section 1 — Preamble", H1_STYLE),
        _p("This Master Circular consolidates instructions issued by the Reserve Bank of India (RBI) "
           "on loans and advances, including restrictions on grant of loans, interest rates, prepayment "
           "charges, and priority sector lending norms. All scheduled commercial banks are required to "
           "comply with the provisions of this circular.", BODY_STYLE),
        _sp(),
        _p("Section 2 — Interest Rate Policy", H1_STYLE),
        _p("Section 2.1 — Floating Rate Loans", H2_STYLE),
        _p("Banks shall not charge foreclosure charges or pre-payment penalties on all floating rate "
           "term loans sanctioned to individual borrowers. This directive applies irrespective of the "
           "source of funds used for pre-payment, whether own funds or funds raised from other lenders. "
           "The prohibition covers home loans, vehicle loans, personal loans, and education loans offered "
           "to individuals on floating interest rate basis.", BODY_STYLE),
        _p("Section 2.2 — Fixed Rate Loans", H2_STYLE),
        _p("For fixed rate loans, banks may levy a foreclosure charge not exceeding 2% of the "
           "outstanding principal at the time of foreclosure. Banks must disclose the foreclosure charge "
           "clearly in the loan agreement and in the Key Fact Statement (KFS) provided at the time of "
           "loan sanction.", BODY_STYLE),
        _sp(),
        _p("Section 3 — Priority Sector Lending", H1_STYLE),
        _p("Section 3.1 — Targets", H2_STYLE),
        _p("Domestic commercial banks and foreign banks with 20 or more branches are required to "
           "maintain 40% of Adjusted Net Bank Credit (ANBC) or Credit Equivalent of Off-Balance Sheet "
           "Exposures (CEOBE), whichever is higher, as priority sector lending. Sub-targets include: "
           "Agriculture: 18%, Micro Enterprises: 7.5%, Weaker Sections: 12%.", BODY_STYLE),
        _sp(),
        _p("Section 4 — Home Loan Regulations", H1_STYLE),
        _p("Section 4.1 — Loan-to-Value Ratio", H2_STYLE),
        _p("The Loan-to-Value (LTV) ratio for individual housing loans shall not exceed the following "
           "limits: (a) Loans up to Rs. 30 lakhs — LTV not to exceed 90%; (b) Loans above Rs. 30 lakhs "
           "and up to Rs. 75 lakhs — LTV not to exceed 80%; (c) Loans above Rs. 75 lakhs — LTV not to "
           "exceed 75%. The cost of the property shall include the stamp duty and registration charges.", BODY_STYLE),
        _p("Section 4.2 — Foreclosure Charges", H2_STYLE),
        _p("As per RBI guidelines, banks cannot charge foreclosure charges on floating rate home loans "
           "to individual borrowers. Any bank found imposing such charges is in violation of RBI "
           "directives and the borrower may lodge a complaint with the Banking Ombudsman. The "
           "Ombudsman scheme provides a free, expeditious alternative dispute resolution mechanism "
           "for bank customers.", BODY_STYLE),
        PageBreak(),
        _p("Section 5 — KYC and Documentation", H1_STYLE),
        _p("All borrowers must complete Know Your Customer (KYC) verification before loan disbursement. "
           "Acceptable KYC documents include Aadhaar card, PAN card, passport, voter ID, and driving "
           "licence. Banks must verify these documents through official channels and maintain records "
           "for a minimum period of 5 years after the loan is closed.", BODY_STYLE),
        _sp(),
        _p("Section 6 — Grievance Redressal", H1_STYLE),
        _p("Banks must establish a structured grievance redressal mechanism. Customer complaints must "
           "be acknowledged within 3 working days and resolved within 30 days. Unresolved complaints "
           "can be escalated to the Banking Ombudsman. Contact: ombudsman@rbi.org.in | "
           "Toll free: 14448.", BODY_STYLE),
    ]
    make_pages = 12
    for i in range(make_pages):
        e.extend([
            _p(f"Section {7 + i} — Additional Provisions {i + 1}", H1_STYLE),
            _p("Banks shall ensure that all loan products are transparent and clearly communicated to "
               "borrowers. The Annual Percentage Rate (APR) must be disclosed upfront. Processing fees "
               "shall not exceed 1% of the loan amount for retail loans. Insurance bundled with loans "
               "must be optional and not a condition for loan approval. Banks offering secured loans "
               "must register the charge with the relevant registry within 30 days of disbursement.", BODY_STYLE),
            _sp(),
        ])
    _build_pdf("RBI_Loans_and_Advances.pdf", e)


# ── 2. RBI KYC Master Directions ─────────────────────────────────────────────

def make_rbi_kyc():
    e = [
        _p("Reserve Bank of India", TITLE_STYLE),
        _p("Master Direction — Know Your Customer (KYC) Directions, 2016 (Updated 2024)", TITLE_STYLE),
        _p("Ref: RBI/2016-17/19 | DBR.AML.BC.No.81/14.01.001/2015-16", SMALL_STYLE),
        _sp(2),
        _p("Section 1 — Introduction", H1_STYLE),
        _p("The Reserve Bank of India, having considered it necessary in the public interest and in the "
           "interest of prevention of money-laundering, issues these Directions under the powers "
           "conferred by Section 35A of the Banking Regulation Act, 1949. All Regulated Entities (REs) "
           "shall comply with these Directions.", BODY_STYLE),
        _sp(),
        _p("Section 2 — Customer Due Diligence (CDD)", H1_STYLE),
        _p("Section 2.1 — Identification Requirements", H2_STYLE),
        _p("REs shall undertake Customer Due Diligence (CDD) measures while establishing a business "
           "relationship and carrying out occasional transactions above the threshold. CDD includes: "
           "(a) identifying and verifying the identity of customers; (b) identifying the beneficial "
           "owner and taking reasonable measures to verify identity; (c) understanding and obtaining "
           "information on the purpose of the business relationship.", BODY_STYLE),
        _p("Section 2.2 — Aadhaar-Based eKYC", H2_STYLE),
        _p("REs may use Aadhaar-based e-KYC for customer identification with the consent of the "
           "customer. The OTP-based e-KYC is permitted for accounts with transaction limits. "
           "Biometric-based e-KYC allows full-service accounts. REs must ensure data localisation "
           "and comply with UIDAI guidelines.", BODY_STYLE),
        _sp(),
        _p("Section 3 — Risk Categorisation", H1_STYLE),
        _p("REs shall categorise customers as low, medium, or high risk based on the nature of "
           "business, transaction patterns, country of origin, and customer profile. High-risk "
           "customers must undergo Enhanced Due Diligence (EDD). Politically Exposed Persons (PEPs) "
           "are automatically classified as high-risk.", BODY_STYLE),
    ]
    for i in range(15):
        e.extend([
            _p(f"Section {4 + i} — Direction {i + 1}", H1_STYLE),
            _p("REs shall maintain records of all KYC documents obtained from customers. These records "
               "shall be maintained for a period of five years from the date of cessation of the "
               "business relationship, or ten years from the date of the transaction, whichever is later. "
               "Periodic review of customer accounts must be conducted based on risk category: "
               "high-risk accounts every 2 years, medium-risk every 8 years, low-risk every 10 years.", BODY_STYLE),
            _sp(),
        ])
    _build_pdf("RBI_KYC_Master_Directions.pdf", e)


# ── 3. IRDAI Health Insurance ─────────────────────────────────────────────────

def make_irdai_health():
    e = [
        _p("Insurance Regulatory and Development Authority of India (IRDAI)", TITLE_STYLE),
        _p("Guidelines on Standardisation of Health Insurance Products", TITLE_STYLE),
        _p("Ref: IRDAI/HLT/REG/CIR/218/09/2024", SMALL_STYLE),
        _sp(2),
        _p("Section 1 — Scope and Applicability", H1_STYLE),
        _p("These guidelines apply to all general and health insurance companies offering health "
           "insurance products in India. All health insurance policies must adhere to the standard "
           "definitions, exclusions, and claim procedures prescribed herein.", BODY_STYLE),
        _sp(),
        _p("Section 2 — Portability", H1_STYLE),
        _p("Section 2.1 — Right to Port", H2_STYLE),
        _p("Every health insurance policyholder has the right to port their policy to another insurer "
           "without losing accrued benefits such as waiting period credits and no-claim bonuses. "
           "Portability request must be made at least 45 days before the renewal date. The new insurer "
           "shall offer coverage at least equivalent to the existing policy benefits.", BODY_STYLE),
        _p("Section 2.2 — Portability Process", H2_STYLE),
        _p("The policyholder must submit a portability form to the new insurer along with existing "
           "policy details. The new insurer must process the portability within 15 days. If the new "
           "insurer does not respond within this period, it is deemed to have accepted the portability "
           "at the same premium as existing policy.", BODY_STYLE),
        _sp(),
        _p("Section 3 — Waiting Periods", H1_STYLE),
        _p("Section 3.1 — Initial Waiting Period", H2_STYLE),
        _p("All health insurance policies must have an initial waiting period of 30 days from the date "
           "of commencement of the policy, during which no claims shall be payable except for "
           "accidental injuries. This waiting period shall not apply on portability.", BODY_STYLE),
        _p("Section 3.2 — Pre-existing Disease Waiting Period", H2_STYLE),
        _p("The maximum waiting period for pre-existing diseases (PED) shall not exceed 36 months "
           "from the date of first policy inception. After continuous renewal for 36 months, all "
           "pre-existing diseases must be covered without any additional loading or exclusion. "
           "Insurers must accept declaration of PED at the time of issuance and cannot reject claims "
           "on grounds of non-disclosure of PED after 8 years of continuous policy.", BODY_STYLE),
        _sp(),
        _p("Section 4 — Claim Settlement", H1_STYLE),
        _p("Insurers must settle cashless claims within 3 hours of receiving the final request from "
           "the hospital. Reimbursement claims must be settled within 30 days of receipt of all "
           "documents. In case of deficiency of documents, the insurer must communicate within 7 days. "
           "Interest at 2% above bank rate is payable if claims are delayed beyond 30 days.", BODY_STYLE),
    ]
    for i in range(15):
        e.extend([
            _p(f"Section {5 + i} — Provision {i + 1}", H1_STYLE),
            _p("Insurers shall not reject claims on technical grounds when the policyholder has acted "
               "in good faith. All rejections must be communicated in writing with specific reasons "
               "citing the policy clause. Policyholders have the right to appeal to the Grievance "
               "Redressal Officer (GRO) within 15 days of rejection. Unresolved complaints can be "
               "taken to the Insurance Ombudsman.", BODY_STYLE),
            _sp(),
        ])
    _build_pdf("IRDAI_Health_Insurance_Guidelines.pdf", e)


# ── 4. SEBI Mutual Fund Regulations ──────────────────────────────────────────

def make_sebi_mf():
    e = [
        _p("Securities and Exchange Board of India (SEBI)", TITLE_STYLE),
        _p("SEBI (Mutual Funds) Regulations, 1996 — Consolidated as amended up to 2024", TITLE_STYLE),
        _p("Ref: SEBI/HO/IMD/MF/CIR/P/2024/0053", SMALL_STYLE),
        _sp(2),
        _p("Section 1 — Definitions", H1_STYLE),
        _p("'Asset Management Company' or 'AMC' means a company formed and registered under the "
           "Companies Act that has been approved by the Board to act as an investment manager to a "
           "mutual fund. 'Net Asset Value' or 'NAV' means the market value of the assets of the "
           "scheme minus its liabilities, divided by the number of units outstanding.", BODY_STYLE),
        _sp(),
        _p("Section 2 — Categorisation of Mutual Fund Schemes", H1_STYLE),
        _p("Section 2.1 — Equity Schemes", H2_STYLE),
        _p("Equity mutual funds must invest a minimum of 65% of total assets in equity and "
           "equity-related instruments. Sub-categories include large-cap (top 100 stocks), mid-cap "
           "(101st to 250th stocks), small-cap (251st stock onwards), and multi-cap funds (minimum "
           "25% each in large, mid, and small cap). Past performance is not indicative of future "
           "returns. Mutual fund investments are subject to market risk.", BODY_STYLE),
        _p("Section 2.2 — Debt Schemes", H2_STYLE),
        _p("Debt mutual funds invest primarily in fixed income instruments. Duration funds carry "
           "interest rate risk; credit risk funds carry default risk. Investors must read the Scheme "
           "Information Document (SID) and Statement of Additional Information (SAI) carefully before "
           "investing.", BODY_STYLE),
        _sp(),
        _p("Section 3 — Expense Ratio", H1_STYLE),
        _p("SEBI has prescribed the maximum Total Expense Ratio (TER) as follows: For equity-oriented "
           "schemes — 2.25% for AUM up to Rs. 500 crore, reducing progressively to 1.05% for AUM "
           "above Rs. 50,000 crore. For other schemes — 2.00% reducing to 0.80%. Direct plans must "
           "have a lower TER than regular plans by at least the distribution commission amount.", BODY_STYLE),
    ]
    for i in range(18):
        e.extend([
            _p(f"Section {4 + i} — Regulation {i + 1}", H1_STYLE),
            _p("AMCs shall publish the portfolio of each scheme on their website within 10 days from "
               "the close of each month. NAV of all schemes shall be calculated and published daily. "
               "AMCs must disclose any material changes to the scheme's fundamental attributes with "
               "30 days' notice to unitholders, giving them the option to exit without exit load. "
               "The redemption proceeds must be credited within 3 business days for equity schemes "
               "and 2 business days for overnight and liquid funds.", BODY_STYLE),
            _sp(),
        ])
    _build_pdf("SEBI_Mutual_Fund_Regulations.pdf", e)


# ── 5. RBI UPI Circular ───────────────────────────────────────────────────────

def make_rbi_upi():
    e = [
        _p("Reserve Bank of India", TITLE_STYLE),
        _p("Guidelines on Unified Payments Interface (UPI) — Safety, Limits, and Fraud Prevention", TITLE_STYLE),
        _p("Ref: RBI/DPSS/2024-25/UPI/Circular/009", SMALL_STYLE),
        _sp(2),
        _p("Section 1 — UPI Transaction Limits", H1_STYLE),
        _p("Section 1.1 — Per Transaction Limit", H2_STYLE),
        _p("The maximum amount per UPI transaction is Rs. 1,00,000 (one lakh). For specific categories "
           "including capital markets, insurance, medical and educational services, the limit is "
           "Rs. 2,00,000 (two lakhs). For tax payments, the limit is Rs. 5,00,000 (five lakhs). "
           "These limits are per transaction and not per day.", BODY_STYLE),
        _p("Section 1.2 — Daily Limits", H2_STYLE),
        _p("Individual banks may set their own daily UPI transaction limits not exceeding "
           "Rs. 1,00,000 per account per day for general categories. Users should check with their "
           "specific bank for applicable daily limits.", BODY_STYLE),
        _sp(),
        _p("Section 2 — UPI Fraud Prevention", H1_STYLE),
        _p("Section 2.1 — Liability on Unauthorised Transactions", H2_STYLE),
        _p("In cases of unauthorised electronic fund transfers, customer liability is determined by "
           "the nature of the deficiency. Where the fault lies with the bank or payment system "
           "provider, the customer bears zero liability. Where the fraud is due to customer negligence "
           "(such as sharing OTP or UPI PIN), the customer bears full liability for losses until "
           "reported to the bank.", BODY_STYLE),
        _p("Section 2.2 — Reporting Timeline", H2_STYLE),
        _p("Customers must report unauthorised transactions to their bank within 3 working days to "
           "avail zero or limited liability benefits. Banks must credit the disputed amount within "
           "10 working days of reporting. The final resolution must be provided within 90 days.", BODY_STYLE),
        _sp(),
        _p("Section 3 — Merchant Payments", H1_STYLE),
        _p("Section 3.1 — Merchant Discount Rate (MDR)", H2_STYLE),
        _p("No MDR shall be charged on UPI and RuPay debit card transactions. This directive applies "
           "to all merchants irrespective of their annual turnover. Any merchant found charging "
           "customers for UPI payments shall be reported to their acquiring bank and NPCI.", BODY_STYLE),
    ]
    for i in range(12):
        e.extend([
            _p(f"Section {4 + i} — Guideline {i + 1}", H1_STYLE),
            _p("Payment System Operators (PSOs) shall implement robust fraud monitoring systems using "
               "AI and machine learning to detect suspicious transactions in real-time. Suspicious "
               "transactions shall be blocked pending customer confirmation. Customers must receive "
               "SMS alerts for all UPI transactions. Banks must provide 24x7 helplines for reporting "
               "fraud. The national cybercrime portal at cybercrime.gov.in can also be used.", BODY_STYLE),
            _sp(),
        ])
    _build_pdf("RBI_UPI_Guidelines.pdf", e)


# ── 6. Sample Home Loan Agreement ────────────────────────────────────────────

def make_home_loan():
    e = [
        _p("SAMPLE HOME LOAN AGREEMENT", TITLE_STYLE),
        _p("Agreement No: HLA/2024/789012", SMALL_STYLE),
        _p("This Home Loan Agreement ('Agreement') is entered into on [DATE] between [BANK NAME], "
           "a scheduled commercial bank incorporated under the Companies Act ('Lender') and the "
           "Borrower(s) named herein.", BODY_STYLE),
        _sp(2),
        _p("Section 1 — Loan Details", H1_STYLE),
        _p("1.1 Loan Amount: Rs. [AMOUNT] (Rupees [AMOUNT IN WORDS] only)\n"
           "1.2 Rate of Interest: [X]% per annum, floating, linked to MCLR/Repo Rate\n"
           "1.3 Loan Tenure: [N] months ([N/12] years)\n"
           "1.4 EMI Amount: Rs. [EMI] per month\n"
           "1.5 Moratorium Period: NIL\n"
           "1.6 First EMI Due Date: [DATE]", BODY_STYLE),
        _sp(),
        _p("Section 2 — Security", H1_STYLE),
        _p("The Borrower shall create an equitable mortgage by deposit of title deeds of the "
           "property described in Schedule I. The mortgage shall secure repayment of the loan "
           "amount, interest, fees, and all other charges payable under this Agreement. The "
           "Lender shall register the mortgage charge with CERSAI within 30 days.", BODY_STYLE),
        _sp(),
        _p("Section 3 — Interest and EMI", H1_STYLE),
        _p("Section 3.1 — Rate Reset", H2_STYLE),
        _p("The floating rate of interest is linked to the bank's MCLR/Repo Rate. The rate shall "
           "be reset periodically as specified in the Sanction Letter. In case of an increase in "
           "the benchmark rate, the Lender may either increase the EMI or extend the tenure. The "
           "Borrower shall be notified of any rate change at least 30 days in advance.", BODY_STYLE),
        _p("Section 4 — Prepayment", H2_STYLE),
        _p("Section 4.1 — No Prepayment Penalty on Floating Rate Loans", H2_STYLE),
        _p("As mandated by RBI guidelines, no prepayment penalty or foreclosure charges shall be "
           "levied on floating rate home loans granted to individual borrowers. The Borrower may "
           "prepay the entire outstanding loan or part thereof at any time without any charge. "
           "Partial prepayments shall first be applied to outstanding interest and then to principal.", BODY_STYLE),
        _p("Section 4.2 — Prepayment Procedure", H2_STYLE),
        _p("To prepay, the Borrower must give 7 days' written notice to the Lender specifying the "
           "amount. The Lender shall provide a prepayment statement within 3 working days. Upon "
           "full repayment, the Lender shall release the title documents within 15 working days "
           "and cancel the mortgage charge with CERSAI.", BODY_STYLE),
    ]
    for i in range(20):
        e.extend([
            _p(f"Section {5 + i} — Clause {i + 1}", H1_STYLE),
            _p("The Borrower represents and warrants that all information provided in the loan "
               "application is true and correct. Any misrepresentation shall entitle the Lender "
               "to recall the loan immediately. The Borrower shall maintain adequate insurance "
               "on the mortgaged property for full replacement value throughout the loan tenure. "
               "The Lender shall be made co-beneficiary on the insurance policy.", BODY_STYLE),
            _sp(),
        ])
    _build_pdf("Sample_Home_Loan_Agreement.pdf", e)


# ── 7. Sample Term Insurance Policy ──────────────────────────────────────────

def make_term_insurance():
    e = [
        _p("SAMPLE TERM INSURANCE POLICY DOCUMENT", TITLE_STYLE),
        _p("Policy No: TI/2024/456789 | Insurer: [INSURER NAME] | IRDAI Reg No: [REG NO]", SMALL_STYLE),
        _sp(2),
        _p("Section 1 — Policy Details", H1_STYLE),
        _p("1.1 Policyholder: [NAME]\n"
           "1.2 Life Assured: [NAME]\n"
           "1.3 Sum Assured: Rs. [AMOUNT]\n"
           "1.4 Policy Term: [N] years\n"
           "1.5 Premium Payment Term: [N] years / Single / Limited\n"
           "1.6 Premium Amount: Rs. [PREMIUM] per [FREQUENCY]\n"
           "1.7 Premium Payment Mode: Annual/Semi-Annual/Quarterly/Monthly", BODY_STYLE),
        _sp(),
        _p("Section 2 — Death Benefit", H1_STYLE),
        _p("Section 2.1 — Lump Sum Payout", H2_STYLE),
        _p("On the death of the Life Assured during the Policy Term, the Insurer shall pay the "
           "Sum Assured to the nominee(s) as a lump sum. The claim must be intimated within "
           "30 days of the death and all required documents submitted within 90 days. "
           "The insurer shall settle the claim within 30 days of receiving complete documents.", BODY_STYLE),
        _p("Section 2.2 — Claim Documents Required", H2_STYLE),
        _p("For death claim: (a) Original Policy Document; (b) Death Certificate issued by competent "
           "authority; (c) Claimant's Statement; (d) Medical Attendant's Certificate (for natural "
           "death); (e) Post Mortem Report, FIR, and Police Investigation Report (for accidental "
           "death). Additional documents may be requested within 7 days of intimation.", BODY_STYLE),
        _sp(),
        _p("Section 3 — Exclusions", H1_STYLE),
        _p("Section 3.1 — Suicide Clause", H2_STYLE),
        _p("If the Life Assured commits suicide within 12 months from the date of commencement or "
           "revival of the policy, the Insurer's liability is limited to 80% of the total premiums "
           "paid, excluding taxes. After 12 months, the full Sum Assured is payable even in case "
           "of suicide. This is as per IRDAI regulations.", BODY_STYLE),
        _p("Section 3.2 — Standard Exclusions", H2_STYLE),
        _p("Death due to the following is excluded: (a) War, invasion, or act of foreign enemy; "
           "(b) Participation in aviation other than as a fare-paying passenger on a licensed "
           "commercial airline; (c) Nuclear contamination. No other exclusions are permitted "
           "except those specifically approved by IRDAI.", BODY_STYLE),
        _sp(),
        _p("Section 4 — Free Look Period", H1_STYLE),
        _p("The policyholder has a free look period of 30 days from the date of receipt of the "
           "policy document. During this period, if the policyholder is not satisfied, they may "
           "return the policy for cancellation and receive a refund of premiums paid after "
           "deducting proportionate risk premium, stamp duty, and medical expenses incurred.", BODY_STYLE),
        _sp(),
        _p("Section 5 — Grace Period and Lapse", H1_STYLE),
        _p("A grace period of 30 days (for annual, semi-annual, quarterly modes) or 15 days "
           "(for monthly mode) is allowed for premium payment. If premium is not paid within "
           "the grace period, the policy lapses and no death benefit is payable during the "
           "lapsed period. A lapsed policy can be revived within 5 years from the due date "
           "of the first unpaid premium.", BODY_STYLE),
    ]
    for i in range(18):
        e.extend([
            _p(f"Section {6 + i} — Provision {i + 1}", H1_STYLE),
            _p("The nominee(s) shall be registered with the insurer at the time of policy issuance. "
               "Changes to the nomination can be made at any time during the policy term. The insurer "
               "shall acknowledge the change within 7 days. If no nomination exists at the time of "
               "death, the benefit shall be paid to the legal heir as per Indian Succession Act.", BODY_STYLE),
            _sp(),
        ])
    _build_pdf("Sample_Term_Insurance_Policy.pdf", e)


def main():
    print("Generating synthetic PDFs...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    make_rbi_loans()
    make_rbi_kyc()
    make_irdai_health()
    make_sebi_mf()
    make_rbi_upi()
    make_home_loan()
    make_term_insurance()

    pdfs = list(OUTPUT_DIR.glob("*.pdf"))
    print(f"\nDone. {len(pdfs)} PDFs created in {OUTPUT_DIR}")
    for p in sorted(pdfs):
        size_kb = p.stat().st_size // 1024
        print(f"  {p.name}: {size_kb} KB")


if __name__ == "__main__":
    main()
