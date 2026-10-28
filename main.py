import copy

class AssetError(Exception):
    pass


class InvalidPriceError(AssetError):

    def __init__(self, price):
        super().__init__(f"Цена не может быть меньше 0: {price}.")


class InvalidMonthsError(AssetError):

    def __init__(self, months):
        super().__init__(f"Месяцы не могут быть отрицательными: {months}. ")


class AssetLimitExceededError(AssetError):

    def __init__(self, employee_name, total_value):
        super().__init__(f"Лимит превышен для сотрудника {employee_name}"
                         f"Общая остаточная стоимость: {total_value} р. (лимит: 150000 р.)")

class ITAsset:
    def __init__(self, asset_id: str, initial_price: float, months_used: int = 0):
        if initial_price <= 0:
            raise InvalidPriceError(initial_price)
        if months_used < 0:
            raise InvalidMonthsError(months_used)

        self.asset_id = asset_id
        self.initial_price = initial_price
        self.months_used = months_used
        self.lifetime_months = 0

    def calculate_residual_value(self) -> float:
        raise NotImplementedError("Метод должен быть переопределен в наследнике")


    def __str__(self):
        residual = self.calculate_residual_value()
        return f"[{self.asset_id}] {self.__class__.__name__} | Остаток: {residual:.2f} руб."

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.asset_id}', price={self.initial_price}, months={self.months_used})"

    def __eq__(self, other):
        if not isinstance(other, ITAsset):
            return NotImplemented
        return self.asset_id == other.asset_id

    def __lt__(self, other):
        return self.calculate_residual_value() < other.calculate_residual_value()

    def __add__(self, other):
        return self.calculate_residual_value() + other.calculate_residual_value()

    def __sub__(self, months: int):
        if months < 0:
            raise InvalidMonthsError(months)

        new_asset = copy.deepcopy(self)
        new_asset.months_used += months
        return new_asset


class Laptop(ITAsset):
    def __init__(self, asset_id: str, initial_price: float, months_used: int = 0):
        super().__init__(asset_id, initial_price, months_used)
        self.lifetime_months = 36

    def calculate_residual_value(self) -> float:
        return self.initial_price * max(0, 1 - (self.months_used / self.lifetime_months))


class Monitor(ITAsset):
    def __init__(self, asset_id: str, initial_price: float, months_used: int = 0):
        super().__init__(asset_id, initial_price, months_used)
        self.lifetime_months = 60  # 5 лет

    def calculate_residual_value(self) -> float:
        return self.initial_price * max(0, 1 - (self.months_used / self.lifetime_months))


class Smartphone(ITAsset):
    def __init__(self, asset_id: str, initial_price: float, months_used: int = 0):
        super().__init__(asset_id, initial_price, months_used)
        self.lifetime_months = 24  # 2 года

    def calculate_residual_value(self) -> float:
        return self.initial_price * max(0, 1 - (self.months_used / self.lifetime_months))


class AssetWarehouse:
    def __init__(self):
        self._assets = []
        self._employee_assignments = {}

    def add_asset(self, asset: ITAsset):
        self._assets.append(asset)

    def assign_to_employee(self, employee_name: str, asset: ITAsset):
        if employee_name not in self._employee_assignments:
            self._employee_assignments[employee_name] = []

        current_total = sum(a.calculate_residual_value() for a in self._employee_assignments[employee_name])
        new_total = current_total + asset.calculate_residual_value()

        if new_total > 150000:
            raise AssetLimitExceededError(employee_name, new_total)

        self._employee_assignments[employee_name].append(asset)
        print(f"УСПЕХ - Техника {asset.asset_id} выдана сотруднику {employee_name}")

    def __len__(self):
        return len(self._assets)

    def __getitem__(self, index):
        return self._assets[index]

if __name__ == "__main__":
    print("1-Создание объектов и склада")
    warehouse = AssetWarehouse()

    laptop1 = Laptop("Ноут1", 85888, 18)
    monitor1 = Monitor("Моник1", 25228, 12)
    phone1 = Smartphone("Телефончик1", 41488, 6)

    warehouse.add_asset(laptop1)
    warehouse.add_asset(monitor1)
    warehouse.add_asset(phone1)

    print(f"2- вывод на экран (__str__ и __repr__) ")
    for asset in warehouse:
        print(f"STR: {asset}")
    print(f"REPR (для отладки): {repr(laptop1)}")

    print(f"3- сортировка (__lt__)")
    print("До сортировки:")
    for asset in warehouse:
        print(f" - {asset.asset_id}: {asset.calculate_residual_value()} руб.")

    sorted_assets = sorted(warehouse)
    print("После сортировки (по возрастанию остаточной стоимости):")
    for asset in sorted_assets:
        print(f" - {asset.asset_id}: {asset.calculate_residual_value()} руб.")

    print(f"4-полиморфный метод в цикле")
    for asset in warehouse:
        print(f"{asset.__class__.__name__} {asset.asset_id} -> Остаток: {asset.calculate_residual_value()} руб.")

    print(f"5-маг методы __add__ и __sub__")
    total_val = laptop1 + phone1
    print(f"сумма остатков ноутбука и смартфона: {total_val} руб.")

    written_off_laptop = laptop1 - 6
    print(f"ноутбук после списания 6 месяцев: {written_off_laptop}")

    print(f"6-работа контейнера (len и getitem)")
    print(f"количество техники на складе (len): {len(warehouse)}")
    print(f"первая техника на складе (index 0): {warehouse[0]}")

    print(f"7-обработка исключений (try/except)")

    try:
        print("даём Иванову: ноутбук, монитор, телефон")
        warehouse.assign_to_employee("Иванов", laptop1)
        warehouse.assign_to_employee("Иванов", monitor1)
        warehouse.assign_to_employee("Иванов", phone1)

        print("даём иванову еще один новый ноутбук")
        laptop2 = Laptop("L-002", 86767, 0)
        warehouse.assign_to_employee("Иванов", laptop2)  #исключение
    except AssetLimitExceededError as e:
        print(f"ошибка лимита: {e}")

    try:
        print("Создание монитора с ценой<0")
        bad_monitor = Monitor("монитор-5кбюджета", -5000)
    except InvalidPriceError as e:
        print(f"ошибка цены: {e}")

    try:
        print("Списываем -10 месяцев")
        laptop1 - (-10)
    except InvalidMonthsError as e:
        print(f"ошибка списания: {e}")
