export type Locale = "en" | "ar";

export type TranslationKey = keyof typeof translations.en;

export const translations = {
  en: {
    // Navigation
    "nav.dashboard": "Dashboard",
    "nav.search": "Search",
    "nav.companies": "Companies",
    "nav.professionals": "Professionals",
    "nav.messages": "Messages",
    "nav.reviews": "Reviews",
    "nav.notifications": "Notifications",
    "nav.profile": "Profile",
    "nav.settings": "Settings",
    "nav.verification": "Verification",
    "nav.shortlist": "Shortlist",
    "nav.adminPanel": "Admin Panel",
    "nav.logout": "Logout",

    // Auth
    "auth.login": "Login",
    "auth.signUp": "Sign Up",
    "auth.email": "Email",
    "auth.password": "Password",
    "auth.firstName": "First Name",
    "auth.lastName": "Last Name",
    "auth.phone": "Phone",
    "auth.accountType": "Account Type",
    "auth.createAccount": "Create Account",
    "auth.signIn": "Sign In",
    "auth.forgotPassword": "Forgot Password?",

    // Dashboard
    "dashboard.welcomeBack": "Welcome back",
    "dashboard.createRfq": "Create RFQ",
    "dashboard.searchSuppliers": "Search Suppliers",
    "dashboard.editProfile": "Edit Profile",
    "dashboard.browseCompanies": "Browse Companies",
    "dashboard.viewIncomingRfqs": "View Incoming RFQs",
    "dashboard.companyProfile": "Company Profile",

    // Common
    "common.loading": "Loading...",
    "common.error": "Error",
    "common.retry": "Retry",
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.submit": "Submit",
    "common.delete": "Delete",
    "common.edit": "Edit",
    "common.back": "Back",
    "common.next": "Next",
    "common.previous": "Previous",

    // Account types
    "accountType.buyer": "Buyer",
    "accountType.supplier": "Supplier",
    "accountType.distributor": "Distributor",
    "accountType.manufacturer": "Manufacturer",
    "accountType.contractor": "Contractor",
    "accountType.subcontractor": "Subcontractor",
    "accountType.individual": "Individual",
  },
  ar: {
    // Navigation
    "nav.dashboard": "\u0644\u0648\u062D\u0629 \u0627\u0644\u062A\u062D\u0643\u0645",
    "nav.search": "\u0628\u062D\u062B",
    "nav.companies": "\u0627\u0644\u0634\u0631\u0643\u0627\u062A",
    "nav.professionals": "\u0627\u0644\u0645\u062A\u062E\u0635\u0635\u0648\u0646",
    "nav.messages": "\u0627\u0644\u0631\u0633\u0627\u0626\u0644",
    "nav.reviews": "\u0627\u0644\u062A\u0642\u064A\u064A\u0645\u0627\u062A",
    "nav.notifications": "\u0627\u0644\u0625\u0634\u0639\u0627\u0631\u0627\u062A",
    "nav.profile": "\u0627\u0644\u0645\u0644\u0641 \u0627\u0644\u0634\u062E\u0635\u064A",
    "nav.settings": "\u0627\u0644\u0625\u0639\u062F\u0627\u062F\u0627\u062A",
    "nav.verification": "\u0627\u0644\u062A\u062D\u0642\u0642",
    "nav.shortlist": "\u0627\u0644\u0642\u0627\u0626\u0645\u0629 \u0627\u0644\u0645\u062E\u062A\u0635\u0631\u0629",
    "nav.adminPanel": "\u0644\u0648\u062D\u0629 \u0627\u0644\u0625\u062F\u0627\u0631\u0629",
    "nav.logout": "\u062A\u0633\u062C\u064A\u0644 \u0627\u0644\u062E\u0631\u0648\u062C",

    // Auth
    "auth.login": "\u062A\u0633\u062C\u064A\u0644 \u0627\u0644\u062F\u062E\u0648\u0644",
    "auth.signUp": "\u0625\u0646\u0634\u0627\u0621 \u062D\u0633\u0627\u0628",
    "auth.email": "\u0627\u0644\u0628\u0631\u064A\u062F \u0627\u0644\u0625\u0644\u0643\u062A\u0631\u0648\u0646\u064A",
    "auth.password": "\u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631",
    "auth.firstName": "\u0627\u0644\u0627\u0633\u0645 \u0627\u0644\u0623\u0648\u0644",
    "auth.lastName": "\u0627\u0644\u0627\u0633\u0645 \u0627\u0644\u0623\u062E\u064A\u0631",
    "auth.phone": "\u0631\u0642\u0645 \u0627\u0644\u0647\u0627\u062A\u0641",
    "auth.accountType": "\u0646\u0648\u0639 \u0627\u0644\u062D\u0633\u0627\u0628",
    "auth.createAccount": "\u0625\u0646\u0634\u0627\u0621 \u062D\u0633\u0627\u0628",
    "auth.signIn": "\u062A\u0633\u062C\u064A\u0644 \u0627\u0644\u062F\u062E\u0648\u0644",
    "auth.forgotPassword": "\u0646\u0633\u064A\u062A \u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631\u061F",

    // Dashboard
    "dashboard.welcomeBack": "\u0645\u0631\u062D\u0628\u0627\u064B \u0628\u0639\u0648\u062F\u062A\u0643",
    "dashboard.createRfq": "\u0625\u0646\u0634\u0627\u0621 \u0637\u0644\u0628 \u0639\u0631\u0636 \u0623\u0633\u0639\u0627\u0631",
    "dashboard.searchSuppliers": "\u0628\u062D\u062B \u0639\u0646 \u0627\u0644\u0645\u0648\u0631\u062F\u064A\u0646",
    "dashboard.editProfile": "\u062A\u0639\u062F\u064A\u0644 \u0627\u0644\u0645\u0644\u0641 \u0627\u0644\u0634\u062E\u0635\u064A",
    "dashboard.browseCompanies": "\u062A\u0635\u0641\u062D \u0627\u0644\u0634\u0631\u0643\u0627\u062A",
    "dashboard.viewIncomingRfqs": "\u0639\u0631\u0636 \u0637\u0644\u0628\u0627\u062A \u0627\u0644\u0639\u0631\u0648\u0636 \u0627\u0644\u0648\u0627\u0631\u062F\u0629",
    "dashboard.companyProfile": "\u0645\u0644\u0641 \u0627\u0644\u0634\u0631\u0643\u0629",

    // Common
    "common.loading": "\u062C\u0627\u0631\u064A \u0627\u0644\u062A\u062D\u0645\u064A\u0644...",
    "common.error": "\u062E\u0637\u0623",
    "common.retry": "\u0625\u0639\u0627\u062F\u0629 \u0627\u0644\u0645\u062D\u0627\u0648\u0644\u0629",
    "common.save": "\u062D\u0641\u0638",
    "common.cancel": "\u0625\u0644\u063A\u0627\u0621",
    "common.submit": "\u0625\u0631\u0633\u0627\u0644",
    "common.delete": "\u062D\u0630\u0641",
    "common.edit": "\u062A\u0639\u062F\u064A\u0644",
    "common.back": "\u0631\u062C\u0648\u0639",
    "common.next": "\u0627\u0644\u062A\u0627\u0644\u064A",
    "common.previous": "\u0627\u0644\u0633\u0627\u0628\u0642",

    // Account types
    "accountType.buyer": "\u0645\u0634\u062A\u0631\u064A",
    "accountType.supplier": "\u0645\u0648\u0631\u062F",
    "accountType.distributor": "\u0645\u0648\u0632\u0639",
    "accountType.manufacturer": "\u0645\u0635\u0646\u0639",
    "accountType.contractor": "\u0645\u0642\u0627\u0648\u0644",
    "accountType.subcontractor": "\u0645\u0642\u0627\u0648\u0644 \u0645\u0646 \u0627\u0644\u0628\u0627\u0637\u0646",
    "accountType.individual": "\u0641\u0631\u062F",
  },
} as const;
