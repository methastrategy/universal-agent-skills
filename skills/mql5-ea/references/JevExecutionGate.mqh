//+------------------------------------------------------------------+
//|                                           JevExecutionGate.mqh   |
//|                   Copyright 2026, Antigravity Institutional Quant |
//|                                     https://github.com/OpenByte  |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Antigravity Institutional Quant"
#property link      "https://github.com/OpenByte"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Class CJevExecutionGate: Atomic Pre-Execution Risk Gatekeeper     |
//+------------------------------------------------------------------+
class CJevExecutionGate
{
private:
   string         m_symbol;
   int            m_max_spread_points;
   double         m_max_daily_dd_pct;
   datetime       m_last_order_bar_time;
   string         m_last_error;
   double         m_initial_daily_equity;
   int            m_last_day_of_year;

   bool           CheckBarLock();
   bool           CheckSpread();
   bool           CheckSessionWindow();
   bool           CheckMarginAndCapital(ENUM_ORDER_TYPE orderType, double plannedLots);

public:
                  CJevExecutionGate(void);
                 ~CJevExecutionGate(void);

   void           Init(string symbol, int maxSpreadPoints, double maxDailyDDPct);
   bool           CheckGate(string symbol, ENUM_ORDER_TYPE orderType, double plannedLots);
   string         GetLastError(void) const { return m_last_error; }
   void           AcknowledgeOrderExecuted(void);
};

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CJevExecutionGate::CJevExecutionGate(void) :
   m_symbol(_Symbol),
   m_max_spread_points(30),
   m_max_daily_dd_pct(5.0),
   m_last_order_bar_time(0),
   m_last_error(""),
   m_initial_daily_equity(0.0),
   m_last_day_of_year(-1)
{
}

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CJevExecutionGate::~CJevExecutionGate(void)
{
}

//+------------------------------------------------------------------+
//| Initialize Gate Configuration                                    |
//+------------------------------------------------------------------+
void CJevExecutionGate::Init(string symbol, int maxSpreadPoints, double maxDailyDDPct)
{
   m_symbol = (symbol == "") ? _Symbol : symbol;
   m_max_spread_points = (maxSpreadPoints <= 0) ? 50 : maxSpreadPoints;
   m_max_daily_dd_pct = (maxDailyDDPct <= 0.0) ? 5.0 : maxDailyDDPct;
   m_initial_daily_equity = AccountInfoDouble(ACCOUNT_EQUITY);
   
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   m_last_day_of_year = dt.day_of_year;
}

//+------------------------------------------------------------------+
//| Check 1: Bar-Level Execution Lock (Prevent Multi-fire on One Bar)|
//+------------------------------------------------------------------+
bool CJevExecutionGate::CheckBarLock(void)
{
   datetime currentBarTime = iTime(m_symbol, PERIOD_CURRENT, 0);
   if(currentBarTime != 0 && currentBarTime == m_last_order_bar_time)
   {
      m_last_error = "Execution blocked: Order already filled on current bar.";
      return false;
   }
   return true;
}

//+------------------------------------------------------------------+
//| Check 2: Spread Spike Guard                                      |
//+------------------------------------------------------------------+
bool CJevExecutionGate::CheckSpread(void)
{
   long currentSpread = SymbolInfoInteger(m_symbol, SYMBOL_SPREAD);
   if(currentSpread > m_max_spread_points)
   {
      m_last_error = StringFormat("Execution blocked: Toxic spread %d points exceeds limit %d points.",
                                  currentSpread, m_max_spread_points);
      return false;
   }
   return true;
}

//+------------------------------------------------------------------+
//| Check 3: Toxic Session / Rollover Guard                          |
//+------------------------------------------------------------------+
bool CJevExecutionGate::CheckSessionWindow(void)
{
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   
   // Rollover window: 23:55 to 00:05
   if((dt.hour == 23 && dt.min >= 55) || (dt.hour == 0 && dt.min <= 5))
   {
      m_last_error = "Execution blocked: Market Rollover high-volatility/spread widening window.";
      return false;
   }
   
   // Monday market open chop: before 01:00
   if(dt.day_of_week == 1 && dt.hour < 1)
   {
      m_last_error = "Execution blocked: Monday market open gap risk window.";
      return false;
   }
   
   // Friday close: after 22:00
   if(dt.day_of_week == 5 && dt.hour >= 22)
   {
      m_last_error = "Execution blocked: Friday weekend close liquidity dry-up.";
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Check 4: Capital & Margin Safety                                 |
//+------------------------------------------------------------------+
bool CJevExecutionGate::CheckMarginAndCapital(ENUM_ORDER_TYPE orderType, double plannedLots)
{
   // Daily Drawdown Reset Check
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   if(dt.day_of_year != m_last_day_of_year)
   {
      m_initial_daily_equity = AccountInfoDouble(ACCOUNT_EQUITY);
      m_last_day_of_year = dt.day_of_year;
   }
   
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(m_initial_daily_equity > 0.0)
   {
      double currentDailyLossPct = ((m_initial_daily_equity - currentEquity) / m_initial_daily_equity) * 100.0;
      if(currentDailyLossPct >= m_max_daily_dd_pct)
      {
         m_last_error = StringFormat("Execution blocked: Max daily drawdown exceeded (%.2f%% >= %.2f%%).",
                                     currentDailyLossPct, m_max_daily_dd_pct);
         return false;
      }
   }
   
   // Free Margin Check
   double requiredMargin = 0.0;
   if(!OrderCalcMargin(orderType, m_symbol, plannedLots, SymbolInfoDouble(m_symbol, SYMBOL_ASK), requiredMargin))
   {
      m_last_error = "Execution blocked: OrderCalcMargin calculation failed.";
      return false;
   }
   
   double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   if(freeMargin < (requiredMargin * 1.5)) // Require 150% margin buffer
   {
      m_last_error = StringFormat("Execution blocked: Insufficient free margin buffer (Req: %.2f, Free: %.2f).",
                                  requiredMargin, freeMargin);
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Master Pre-Execution Gating Function                             |
//+------------------------------------------------------------------+
bool CJevExecutionGate::CheckGate(string symbol, ENUM_ORDER_TYPE orderType, double plannedLots)
{
   m_last_error = "";
   
   if(symbol != m_symbol && symbol != "")
      m_symbol = symbol;
      
   // Full Trading Mode Allowed?
   long tradeMode = SymbolInfoInteger(m_symbol, SYMBOL_TRADE_MODE);
   if(tradeMode != SYMBOL_TRADE_MODE_FULL)
   {
      m_last_error = "Execution blocked: Symbol trading mode is restricted or disabled.";
      return false;
   }

   // Sequential Gating Pipeline
   if(!CheckBarLock()) return false;
   if(!CheckSpread()) return false;
   if(!CheckSessionWindow()) return false;
   if(!CheckMarginAndCapital(orderType, plannedLots)) return false;

   return true;
}

//+------------------------------------------------------------------+
//| Call immediately after OrderSend() succeeds                      |
//+------------------------------------------------------------------+
void CJevExecutionGate::AcknowledgeOrderExecuted(void)
{
   m_last_order_bar_time = iTime(m_symbol, PERIOD_CURRENT, 0);
}
//+------------------------------------------------------------------+
