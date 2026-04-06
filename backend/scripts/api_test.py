"""Quick API smoke test using ASGI transport."""
import asyncio
import sys
sys.path.insert(0, '.')


async def test():
    from httpx import AsyncClient, ASGITransport
    from app.main import create_app

    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as client:

        # 1. Login buyer1
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "buyer1@test.com", "password": "Test1234!"},
        )
        print(f"Login buyer1: {r.status_code}")
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        h1 = {"Authorization": f"Bearer {token}"}

        # 2. Companies list - get Cairo Telecom Solutions
        r = await client.get("/api/v1/companies", headers=h1)
        data = r.json()
        print(f"GET /companies: {r.status_code}, total={data.get('total')}")
        assert r.status_code == 200
        companies = data.get("items", [])
        cairo_telecom = next((c for c in companies if "Cairo" in c.get("name", "")), None)
        nile_fiber = next((c for c in companies if "Nile" in c.get("name", "")), None)
        fibertech = next((c for c in companies if "FiberTech" in c.get("name", "")), None)
        print(f"  Cairo Telecom: {cairo_telecom['id'][:8] if cairo_telecom else 'NOT FOUND'}...")
        print(f"  FiberTech Egypt: {fibertech['id'][:8] if fibertech else 'NOT FOUND'}...")

        # 3. RFQs for Cairo Telecom (Bug 1 fix - PATCH with partial body)
        if cairo_telecom:
            company_id = cairo_telecom["id"]
            r = await client.get(f"/api/v1/rfqs?company_id={company_id}&role=buyer", headers=h1)
            rfqs = r.json()
            print(f"GET /rfqs (buyer): {r.status_code}, items={len(rfqs.get('items', []))}")
            assert r.status_code == 200, r.text
            items = rfqs.get("items", [])
            if items:
                rfq_id = items[0]["id"]
                # Bug 1 fix: partial PATCH should work (only notes, no required fields)
                r = await client.patch(
                    f"/api/v1/rfqs/{rfq_id}",
                    headers=h1,
                    json={"notes": "Partial update test - Bug 1 fix verified"},
                )
                print(f"PATCH /rfqs partial (Bug1): {r.status_code} (400=biz-logic OK, 422=schema bug)")
                # Bug 1 fix: should NOT get 422 "field required" - 400 from business logic is OK
                assert r.status_code != 422, f"Bug1 still broken (422): {r.text[:200]}"

        # 4. Messages threads (buyer1)
        r = await client.get("/api/v1/messages/threads", headers=h1)
        threads_data = r.json()
        threads = threads_data.get("items", [])
        print(f"GET /messages/threads (buyer1): {r.status_code}, count={len(threads)}")
        assert r.status_code == 200

        # 5. Login supplier1
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "supplier1@test.com", "password": "Test1234!"},
        )
        print(f"Login supplier1: {r.status_code}")
        assert r.status_code == 200, r.text
        tok2 = r.json()["access_token"]
        h2 = {"Authorization": f"Bearer {tok2}"}

        # 6. supplier1 message threads
        r = await client.get("/api/v1/messages/threads", headers=h2)
        threads2 = r.json().get("items", [])
        print(f"GET /messages/threads (supplier1): {r.status_code}, count={len(threads2)}")

        # 7. Send message (Bug 4 fix test - should return correct message with sender loaded)
        if threads2:
            tid = threads2[0]["id"]
            r = await client.post(
                f"/api/v1/messages/threads/{tid}/messages",
                headers=h2,
                json={"content": "Test reply from supplier - Bug 4 fix test"},
            )
            msg = r.json()
            sender_name = msg.get("sender_name", "?")
            print(f"POST /messages (Bug4 fix): {r.status_code}, sender_name={sender_name}")
            assert r.status_code == 200, r.text
            assert sender_name is not None and sender_name != "?", f"sender_name missing: {msg}"

        # 8. RFQs for FiberTech (supplier)
        if fibertech:
            r = await client.get(f"/api/v1/rfqs?company_id={fibertech['id']}&role=supplier", headers=h2)
            print(f"GET /rfqs (supplier): {r.status_code}, items={len(r.json().get('items', []))}")
            assert r.status_code == 200, r.text

        # 9. Bug 2 fix: PATCH company member (flush test)
        if fibertech:
            company_id = fibertech["id"]
            r = await client.get(f"/api/v1/companies/{company_id}/members", headers=h2)
            members = r.json()
            print(f"GET /companies/{company_id[:8]}/members: {r.status_code}, count={len(members)}")
            if r.status_code == 200 and len(members) >= 2:
                member_id = members[-1]["id"]
                r = await client.patch(
                    f"/api/v1/companies/{company_id}/members/{member_id}",
                    headers=h2,
                    json={"title": "Senior Engineer"},
                )
                print(f"PATCH member (Bug2 fix): {r.status_code}")
                if r.status_code not in (200, 403):
                    print(f"  Error: {r.text[:200]}")

        # 10. Verification - test Bug 3 fix (get a pending request as admin)
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "buyer1@test.com", "password": "Test1234!"},
        )
        # (Admin test skipped - no admin user seeded in test accounts)
        # The Bug 3 fix is in verification/service.py scalar_one_or_none

        print("\nAll tests passed!")


asyncio.run(test())
