"""AI2 kill test: trained stimulus-only controller vs planted visibility floor.
See docs/prereg/2026-11-21_self_model_kill_trained_control.md."""
import json
import torch

torch.set_num_threads(3)
S = torch.arange(21) / 20.0
CELLS = [(0.95, 0.5, 0.1, 0.02), (0.95, 1.0, 0.1, 0.02), (0.8, 0.5, 0.3, 0.1), (0.95, 0.5, 0.3, 0.1)]


def sample(n, sigma, gen):
    s = S[torch.randint(0, 21, (n,), generator=gen)]
    x = s + sigma * torch.randn(n, generator=gen)
    return s, x


def loss_of(a, s, e, g, k, gen):
    cap = (torch.rand(s.shape, generator=gen) < s ** g).float()
    return cap * (1 - e * a) + k * a


def run(cell, floor, seed):
    e, g, sigma, k = cell
    gen = torch.Generator().manual_seed(seed)
    torch.manual_seed(seed)
    net = torch.nn.Sequential(torch.nn.Linear(1, 16), torch.nn.Tanh(), torch.nn.Linear(16, 16), torch.nn.Tanh(), torch.nn.Linear(16, 1))
    opt = torch.optim.Adam(net.parameters(), lr=0.01)
    inp = (lambda x: torch.where(x < 0.3, torch.zeros_like(x), x)) if floor else (lambda x: x)
    for _ in range(1500):
        s, x = sample(4096, sigma, gen)
        p = torch.sigmoid(net(inp(x)[:, None]).squeeze(1))
        a = torch.bernoulli(p.detach(), generator=gen)
        r = -loss_of(a, s, e, g, k, gen)
        logp = a * torch.log(p + 1e-8) + (1 - a) * torch.log(1 - p + 1e-8)
        opt.zero_grad()
        (-(r - r.mean()) * logp).mean().backward()
        opt.step()
    D = []
    with torch.no_grad():
        for sv in S:
            s = torch.full((20000,), float(sv))
            x = s + sigma * torch.randn(20000, generator=gen)
            a = (torch.sigmoid(net(inp(x)[:, None]).squeeze(1)) > 0.5).float()
            D.append(float(loss_of(a, s, e, g, k, gen).mean()))
    i = max(range(21), key=lambda j: D[j])
    r = D[i] - D[-1]
    return {"D": [round(d, 4) for d in D], "reversal": round(r, 4), "peak_s": float(S[i]), "shows": bool(r > 0.05 and S[i] < 0.9)}


out = {"cells": []}
for cell in CELLS:
    row = {"cell": cell}
    for name, floor in (("T", False), ("TF", True)):
        rs = [run(cell, floor, seed) for seed in range(4)]
        row[name] = {"seeds": rs, "n_show": sum(r["shows"] for r in rs), "cell_shows": sum(r["shows"] for r in rs) >= 3}
    out["cells"].append(row)
    print(cell, "T", [r["reversal"] for r in row["T"]["seeds"]], "TF", [r["reversal"] for r in row["TF"]["seeds"]], flush=True)
t_cells = sum(c["T"]["cell_shows"] for c in out["cells"])
tf_cells = sum(c["TF"]["cell_shows"] for c in out["cells"])
planted = tf_cells >= 3
out.update(T_cells=t_cells, TF_cells=tf_cells, planted_pass=planted,
           verdict="void" if not planted else ("step 0 holds: reversal needs a visibility floor" if t_cells <= 1 else "reviewer right: reversal not diagnostic"))
json.dump(out, open("kill_trained.json", "w"), indent=1)
print("T cells", t_cells, "TF cells", tf_cells, "->", out["verdict"])
