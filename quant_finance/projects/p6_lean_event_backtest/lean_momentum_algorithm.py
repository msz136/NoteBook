from AlgorithmImports import *


class AuditedMomentumAlgorithm(QCAlgorithm):
    """LEAN-compatible skeleton; requires official LEAN runtime to execute."""

    def initialize(self):
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2020, 12, 31)
        self.set_cash(100000)
        self.symbol = self.add_equity("SPY", Resolution.DAILY).symbol
        self.securities[self.symbol].set_fee_model(ConstantFeeModel(1.0))
        self.securities[self.symbol].set_slippage_model(ConstantSlippageModel(0.0002))
        self.window = RollingWindow[float](6)

    def on_data(self, data: Slice):
        if not data.bars.contains_key(self.symbol):
            return
        close = data.bars[self.symbol].close
        self.window.add(close)
        if not self.window.is_ready:
            return
        momentum = self.window[0] / self.window[5] - 1
        target = 0.5 if momentum > 0 else 0.0
        self.set_holdings(self.symbol, target)

    def on_order_event(self, order_event: OrderEvent):
        if order_event.status in (OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED):
            self.debug(f"ORDER_EVENT,{order_event.order_id},{order_event.status},{order_event.fill_quantity},{order_event.fill_price}")
