import numpy as np
# Building a prediction market
# https://learn.microsoft.com/en-us/archive/msdn-magazine/2016/june/test-run-introduction-to-prediction-markets


class Market:

    def __int__(self, name: str, liquidity: float = 100.0, team_a_shares: int = 0, team_b_shares: int = 0, cost: float = 0.5012):
        self.name = name
        self.liquidity = liquidity

        self.team_a_shares = team_a_shares
        self.team_b_shares = team_b_shares

        self.probabilities = (0.5, 0.5)

        self.a_cost = cost
        self.b_cost = cost

    def purchase_shares(self, side, quantity):
        pass

    @staticmethod
    def cost(x: int, y: int, liq: float):
        return liq * np.log(np.exp(x/liq) + np.exp(y/liq))

    def txn_cost(self, outstanding: list, idx: int, shares: int, liq: float):
        """
        static double CostOfTrans(int[] outstanding, int idx, int nShares, double liq)
        {
          int[] after = new int[2];
          Array.Copy(outstanding, after, 2);
          after[idx] += nShares;
          return Cost(after, liq) - Cost(outstanding, liq);
        }
        :return:
        """
        """C(20+30, 10) - C(20, 10) = C(50, 10) - C(20, 10) = 101.30 - 84.44 = $16.86"""
        after = outstanding.copy()
        after[idx] += shares

        return self.cost(after, liq) - self.cost(outstanding, liq)



    """100.0 * ln(exp(20/100) + exp(10/100)) = 100.0 * ln(1.22 + 1.11) = 100.0 * 0.8444 = $84.44"""

    """static double Cost(int[] outstanding, double liq)
{
  double sum = 0.0;
  for (int i = 0; i < 2; ++i)
    sum += Math.Exp(outstanding[i] / liq);
  return liq * Math.Log(sum);
}"""

    def calc_probability(self):
        pass