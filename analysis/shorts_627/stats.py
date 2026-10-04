import numpy as np, pandas as pd
from scipy.stats import spearmanr, mannwhitneyu

d = pd.read_csv('features.csv')
d = d[d.views.notna() & (d.views > 0)].copy()
# 新しすぎる動画は再生数がまだ伸びきっていないので、各チャンネル最新3本を除外
d = d[d.idx > 3]
# チャンネル内の中央値で割る = 「そのチャンネルの普段より何倍伸びたか」
d['rel'] = np.log10(d.views / d.groupby('channel').views.transform('median'))
d['ocr_any'] = (d.ocr_words > 0).astype(int)
d['face_any'] = (d.faces > 0).astype(int)
d['face_big'] = (d.face_area > 0.05).astype(int)
print('n =', len(d), 'channels =', d.channel.nunique())
print('views median', int(d.views.median()))

feats = ['t_len', 't_emoji', 't_hash', 't_q', 't_ex', 't_num', 't_caps', 't_you', 't_i', 't_vs', 't_pov',
         'bright', 'contrast', 'sat', 'colorful', 'edge_density', 'red_share',
         'faces', 'face_any', 'face_big', 'face_area', 'ocr_words', 'ocr_any']
res = []
for f in feats:
    x = d[[f, 'rel']].dropna()
    if x[f].nunique() < 2:
        continue
    rho, p = spearmanr(x[f], x.rel)
    if set(x[f].unique()) <= {0, 1}:
        a, b = x[x[f] == 1].rel, x[x[f] == 0].rel
        eff = 10 ** (a.median() - b.median())
        share = len(a) / len(x)
        p = mannwhitneyu(a, b).pvalue if len(a) > 4 else np.nan
    else:
        hi = x[x[f] >= x[f].quantile(.75)].rel.median()
        lo = x[x[f] <= x[f].quantile(.25)].rel.median()
        eff = 10 ** (hi - lo)
        share = np.nan
    res.append((f, round(rho, 3), round(p, 4), round(eff, 2), None if np.isnan(share) else round(share, 2)))
r = pd.DataFrame(res, columns=['feature', 'spearman', 'p', 'effect_x', 'share']).sort_values('p')
print(r.to_string(index=False))

# 上位25% vs 下位25%（チャンネル内相対）の平均プロファイル
top = d[d.rel >= d.rel.quantile(.75)]
bot = d[d.rel <= d.rel.quantile(.25)]
cols = ['t_len', 't_emoji', 't_q', 't_ex', 't_num', 'face_any', 'face_big', 'ocr_any', 'bright', 'colorful', 'sat', 'contrast']
print(pd.DataFrame({'top25': top[cols].mean(), 'bottom25': bot[cols].mean(), 'all': d[cols].mean()}).round(3))

print('\n--- 全体の分布 ---')
print('title len median', d.t_len.median(), '| emoji share', round((d.t_emoji > 0).mean(), 2),
      '| hashtag share', round((d.t_hash > 0).mean(), 2), '| face share', round(d.face_any.mean(), 2),
      '| cover text share', round(d.ocr_any.mean(), 2))
print('\n--- チャンネル内で最も伸びた10本 ---')
print(d.sort_values('rel', ascending=False)[['channel', 'title', 'views', 'rel']].head(10).to_string(index=False))
