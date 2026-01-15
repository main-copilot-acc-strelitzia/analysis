import sys, os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
	sys.path.insert(0, project_root)

from analysis.general import analyzer
from analysis.forex import trend

print('trend.TrendAnalysis has attr:', hasattr(trend.TrendAnalysis, 'trend_strength_confirmation'))
print('analyzer.TrendAnalysis is', analyzer.TrendAnalysis)
print('Same object?:', analyzer.TrendAnalysis is trend.TrendAnalysis)
