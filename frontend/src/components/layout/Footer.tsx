import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-muted/50 mt-auto">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-semibold text-sm mb-3">FiberHub Egypt</h3>
            <p className="text-xs text-muted-foreground">
              Egypt&apos;s trusted B2B platform for the fiber optic sector.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-sm mb-3">Platform</h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li><Link href="/search" className="hover:text-foreground">Search</Link></li>
              <li><Link href="/search?type=companies" className="hover:text-foreground">Companies</Link></li>
              <li><Link href="/search?type=professionals" className="hover:text-foreground">Professionals</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-sm mb-3">Company</h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li><Link href="#" className="hover:text-foreground">About</Link></li>
              <li><Link href="#" className="hover:text-foreground">Contact</Link></li>
              <li><Link href="#" className="hover:text-foreground">Terms</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-sm mb-3">Support</h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li><Link href="#" className="hover:text-foreground">Help Center</Link></li>
              <li><Link href="#" className="hover:text-foreground">Privacy Policy</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t pt-4 text-center text-xs text-muted-foreground">
          &copy; {new Date().getFullYear()} FiberHub Egypt. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
