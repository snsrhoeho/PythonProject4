# file: main.py
from uuid import uuid4
from time import sleep

# ────────────── 도메인 모델 ──────────────
class Order:
    def __init__(self, user_name: str, store: str, items: list[tuple[str, int, int]]):
        self.id = str(uuid4())[:8]
        self.user_name = user_name
        self.store = store
        self.items = items        # (메뉴명, 수량, 단가)
        self.amount = sum(q * p for _, q, p in items)
        self.status = "NEW"


class PaymentGateway:
    def pay(self, card_number: str, amount: int) -> bool:
        print(f"[PG] 카드({card_number[-4:]})로 {amount:,}원 결제 시도")
        sleep(0.7)
        print("[PG] 결제 성공")
        return True


class DeliveryRider:
    def __init__(self, name: str):
        self.name = name

    def deliver(self, order: Order):
        print(f"[Rider {self.name}] 주문 {order.id} 픽업 → 배달 출발")
        sleep(1)
        print(f"[Rider {self.name}] 고객에게 배달 완료")


class Restaurant:
    def __init__(self, name: str, menu: dict[str, int], rider: DeliveryRider):
        self.name = name
        self.menu = menu
        self.rider = rider

    def accept_order(self, order: Order):
        print(f"[Restaurant] '{self.name}' ▶ 주문 {order.id} 접수, 조리 시작")
        sleep(1.2)
        self.rider.deliver(order)


# ────────────── 앱 파사드 ──────────────
class YogiyoApp:
    def __init__(self, stores: list[Restaurant], pg: PaymentGateway):
        self.stores = stores
        self.pg = pg

    # ---- 검색 & 선택 ----
    def search_store(self, keyword: str) -> list[Restaurant]:
        return [s for s in self.stores if keyword in s.name or keyword in "치킨"]  # 간단 필터

    def choose_store(self, stores: list[Restaurant]) -> Restaurant:
        for idx, s in enumerate(stores, 1):
            print(f"{idx}. {s.name}")
        while True:
            pick = input("가게 번호 선택: ")
            if pick.isdigit() and 1 <= int(pick) <= len(stores):
                return stores[int(pick) - 1]
            print("❗ 올바른 번호를 입력하세요.")

    # ---- 장바구니 ----g
    def pick_menu_items(self, store: Restaurant) -> list[tuple[str, int, int]]:
        items = []
        print(f"\n📜 {store.name} 메뉴")
        menu_keys = list(store.menu.keys())
        for idx, m in enumerate(menu_keys, 1):
            print(f"{idx}. {m} – {store.menu[m]:,}원")
        print("0. 주문 완료")

        while True:
            choice = input("메뉴 번호 (0 종료): ")
            if choice == "0":
                break
            if choice.isdigit() and 1 <= int(choice) <= len(menu_keys):
                qty = input("수량: ")
                if qty.isdigit() and int(qty) > 0:
                    menu_name = menu_keys[int(choice) - 1]
                    items.append((menu_name, int(qty), store.menu[menu_name]))
                else:
                    print("❗ 수량은 1 이상 숫자로 입력")
            else:
                print("❗ 올바른 번호를 입력")
        return items

    # ---- 결제 & 주문 ----
    def checkout(self, user_name: str, store: Restaurant, items: list[tuple[str, int, int]]):
        order = Order(user_name, store.name, items)
        print(f"\n🧾 주문 금액 합계: {order.amount:,}원")
        pay_type = input("결제 방식 선택 (card / cash): ").strip().lower()
        if pay_type == "card":
            card_no = input("카드 번호 입력(****-****-****-****): ")
            if not self.pg.pay(card_no, order.amount):
                print("결제 실패. 주문 취소")
                return
        else:
            print("[App] 현금 결제 선택됨 (배달 시 지불)")

        order.status = "PAID"
        store.accept_order(order)
        order.status = "DELIVERED"
        print(f"[User] 주문 완료! 번호={order.id}")

    # ---- 전체 흐름 ----
    def order_flow(self, user_name: str):
        keyword = input("🔍 검색어 입력(예: 치킨): ")
        stores = self.search_store(keyword)
        if not stores:
            print("검색 결과가 없습니다.")
            return

        print("\n🔎 가게 리스트")
        store = self.choose_store(stores)

        items = self.pick_menu_items(store)
        if not items:
            print("장바구니가 비어 있어 주문을 종료합니다.")
            return

        self.checkout(user_name, store, items)


# ────────────── 실행 스크립트 ──────────────
if __name__ == "__main__":
    rider = DeliveryRider("철수")
    stores = [
        Restaurant("네네치킨 구로점", {"후라이드": 17000, "양념": 18000, "반반": 18000}, rider),
        Restaurant("BHC 신도림점", {"뿌링클": 19000, "맛초킹": 20000}, rider),
        Restaurant("또봉이치킨 1호점", {"또봉이후라이드": 16000, "간장": 17000}, rider),
    ]
    app = YogiyoApp(stores, PaymentGateway())

    print("=== 요기요 모의 주문 CLI ===")
    user_name = input("이름 입력: ")
    app.order_flow(user_name)
