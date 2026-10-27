//+------------------------------------------------------------------+
//|                                         QuantPlaybookSignals.mqh |
//|                   Copyright 2026, Quantitative Signal Engine     |
//|               https://github.com/storytold / ArtCraft Inspired   |
//+------------------------------------------------------------------+
#property copyright "Quantitative Trading Engine"
#property link      "https://github.com/storytold"
#property strict

#ifndef QUANT_PLAYBOOK_SIGNALS_MQH
#define QUANT_PLAYBOOK_SIGNALS_MQH

enum ENUM_PLAYBOOK_STRATEGY
{
   STRAT_NONE                 = 0,
   STRAT_SMC_LIQUIDITY_SWEEP  = 1,
   STRAT_FVG_RETEST           = 2,
   STRAT_ASIAN_BREAKOUT       = 3,
   STRAT_EMA_PULLBACK         = 4,
   STRAT_BOLLINGER_SQUEEZE    = 5
};

struct PlaybookSignal
{
   bool                    is_valid;
   ENUM_PLAYBOOK_STRATEGY  strategy;
   ENUM_ORDER_TYPE         order_type;      // ORDER_TYPE_BUY or ORDER_TYPE_SELL
   double                  entry_price;
   double                  stop_loss;
   double                  take_profit;
   double                  risk_reward_ratio;
   string                  rationale;
};

//+------------------------------------------------------------------+
//| 1. SMC Liquidity Sweep + BOS Check                               |
//+------------------------------------------------------------------+
PlaybookSignal CheckLiquiditySweep(const string symbol, ENUM_TIMEFRAMES tf, int lookback_bars=20)
{
   PlaybookSignal sig;
   ZeroMemory(sig);
   sig.strategy = STRAT_SMC_LIQUIDITY_SWEEP;
   
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if(CopyRates(symbol, tf, 0, lookback_bars + 2, rates) < lookback_bars + 2)
      return sig;
      
   double highest_high = 0.0;
   double lowest_low = DBL_MAX;
   for(int i = 2; i <= lookback_bars; i++)
   {
      if(rates[i].high > highest_high) highest_high = rates[i].high;
      if(rates[i].low < lowest_low) lowest_low = rates[i].low;
   }
   
   // Bearish Sweep: Wick above previous high, but closed below it
   if(rates[1].high > highest_high && rates[1].close < highest_high)
   {
      sig.is_valid = true;
      sig.order_type = ORDER_TYPE_SELL;
      sig.entry_price = rates[0].open;
      sig.stop_loss = rates[1].high + (10 * SymbolInfoDouble(symbol, SYMBOL_POINT));
      double risk = MathAbs(sig.entry_price - sig.stop_loss);
      sig.take_profit = sig.entry_price - (2.0 * risk);
      sig.risk_reward_ratio = 2.0;
      sig.rationale = "Bearish SMC Liquidity Sweep detected above previous high";
      return sig;
   }
   
   // Bullish Sweep: Wick below previous low, but closed above it
   if(rates[1].low < lowest_low && rates[1].close > lowest_low)
   {
      sig.is_valid = true;
      sig.order_type = ORDER_TYPE_BUY;
      sig.entry_price = rates[0].open;
      sig.stop_loss = rates[1].low - (10 * SymbolInfoDouble(symbol, SYMBOL_POINT));
      double risk = MathAbs(sig.entry_price - sig.stop_loss);
      sig.take_profit = sig.entry_price + (2.0 * risk);
      sig.risk_reward_ratio = 2.0;
      sig.rationale = "Bullish SMC Liquidity Sweep detected below previous low";
      return sig;
   }
   
   return sig;
}

//+------------------------------------------------------------------+
//| 2. Fair Value Gap (FVG) Retest Check                             |
//+------------------------------------------------------------------+
PlaybookSignal CheckFairValueGap(const string symbol, ENUM_TIMEFRAMES tf)
{
   PlaybookSignal sig;
   ZeroMemory(sig);
   sig.strategy = STRAT_FVG_RETEST;
   
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if(CopyRates(symbol, tf, 0, 5, rates) < 5)
      return sig;
      
   // Bullish FVG: Low of bar 1 is higher than High of bar 3
   if(rates[2].low > rates[4].high)
   {
      double fvg_top = rates[2].low;
      double fvg_bottom = rates[4].high;
      double midpoint = (fvg_top + fvg_bottom) / 2.0;
      
      // Current bar retests the midpoint
      if(rates[1].low <= midpoint && rates[1].close > midpoint)
      {
         sig.is_valid = true;
         sig.order_type = ORDER_TYPE_BUY;
         sig.entry_price = rates[0].open;
         sig.stop_loss = fvg_bottom - (10 * SymbolInfoDouble(symbol, SYMBOL_POINT));
         double risk = MathAbs(sig.entry_price - sig.stop_loss);
         sig.take_profit = sig.entry_price + (2.5 * risk);
         sig.risk_reward_ratio = 2.5;
         sig.rationale = "Bullish FVG Retest confirmed at 50% midpoint";
         return sig;
      }
   }
   
   // Bearish FVG: High of bar 1 is lower than Low of bar 3
   if(rates[2].high < rates[4].low)
   {
      double fvg_top = rates[4].low;
      double fvg_bottom = rates[2].high;
      double midpoint = (fvg_top + fvg_bottom) / 2.0;
      
      // Current bar retests the midpoint
      if(rates[1].high >= midpoint && rates[1].close < midpoint)
      {
         sig.is_valid = true;
         sig.order_type = ORDER_TYPE_SELL;
         sig.entry_price = rates[0].open;
         sig.stop_loss = fvg_top + (10 * SymbolInfoDouble(symbol, SYMBOL_POINT));
         double risk = MathAbs(sig.entry_price - sig.stop_loss);
         sig.take_profit = sig.entry_price - (2.5 * risk);
         sig.risk_reward_ratio = 2.5;
         sig.rationale = "Bearish FVG Retest confirmed at 50% midpoint";
         return sig;
      }
   }
   
   return sig;
}

//+------------------------------------------------------------------+
//| 3. EMA Triple Trend Pullback Check                               |
//+------------------------------------------------------------------+
PlaybookSignal CheckEMAPullback(const string symbol, ENUM_TIMEFRAMES tf, int h_ema20, int h_ema50, int h_ema200)
{
   PlaybookSignal sig;
   ZeroMemory(sig);
   sig.strategy = STRAT_EMA_PULLBACK;
   
   double ema20[], ema50[], ema200[];
   ArraySetAsSeries(ema20, true);
   ArraySetAsSeries(ema50, true);
   ArraySetAsSeries(ema200, true);
   
   if(CopyBuffer(h_ema20, 0, 0, 3, ema20) < 3 ||
      CopyBuffer(h_ema50, 0, 0, 3, ema50) < 3 ||
      CopyBuffer(h_ema200, 0, 0, 3, ema200) < 3)
      return sig;
      
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if(CopyRates(symbol, tf, 0, 3, rates) < 3)
      return sig;
      
   // Bullish Trend: 20 > 50 > 200
   if(ema20[1] > ema50[1] && ema50[1] > ema200[1])
   {
      // Pullback into pocket (Low touched between EMA20 and EMA50, closed back above EMA20)
      if(rates[1].low <= ema20[1] && rates[1].low >= ema50[1] && rates[1].close > ema20[1])
      {
         sig.is_valid = true;
         sig.order_type = ORDER_TYPE_BUY;
         sig.entry_price = rates[0].open;
         sig.stop_loss = ema50[1] - (10 * SymbolInfoDouble(symbol, SYMBOL_POINT));
         double risk = MathAbs(sig.entry_price - sig.stop_loss);
         sig.take_profit = sig.entry_price + (2.0 * risk);
         sig.risk_reward_ratio = 2.0;
         sig.rationale = "Bullish EMA 20/50 Value Pocket Pullback Rebound";
         return sig;
      }
   }
   
   // Bearish Trend: 20 < 50 < 200
   if(ema20[1] < ema50[1] && ema50[1] < ema200[1])
   {
      // Pullback into pocket (High touched between EMA20 and EMA50, closed back below EMA20)
      if(rates[1].high >= ema20[1] && rates[1].high <= ema50[1] && rates[1].close < ema20[1])
      {
         sig.is_valid = true;
         sig.order_type = ORDER_TYPE_SELL;
         sig.entry_price = rates[0].open;
         sig.stop_loss = ema50[1] + (10 * SymbolInfoDouble(symbol, SYMBOL_POINT));
         double risk = MathAbs(sig.entry_price - sig.stop_loss);
         sig.take_profit = sig.entry_price - (2.0 * risk);
         sig.risk_reward_ratio = 2.0;
         sig.rationale = "Bearish EMA 20/50 Value Pocket Pullback Rejection";
         return sig;
      }
   }
   
   return sig;
}

#endif // QUANT_PLAYBOOK_SIGNALS_MQH
