"""A small z-buffer renderer for the 3D figures. Matplotlib's 3D plots draw whole faces in one
order and get the depth wrong on parts like these, so the views are drawn pixel by pixel here."""
import numpy as np

def view_matrix(elev, azim):
    e, a = np.radians(elev), np.radians(azim)
    d = np.array([np.cos(e)*np.cos(a), np.cos(e)*np.sin(a), np.sin(e)])   # towards the viewer
    up = np.array([0, 0, 1.0]) if abs(e) < np.radians(89) else np.array([0, 1.0, 0])
    r = np.cross(up, d); r /= np.linalg.norm(r); u = np.cross(d, r)
    return np.array([r, u, d])

def render(meshes, elev, azim, size=(1400, 1000), margin=30, light=(0.4, 0.3, 1.0)):
    """meshes: list of (triangles N x 3 x 3, rgb). Returns an RGB image (white background)."""
    M = view_matrix(elev, azim)
    allp = np.concatenate([t.reshape(-1, 3) for t, _ in meshes]) @ M.T
    lo, hi = allp.min(0), allp.max(0)
    W, H = size
    s = min((W-2*margin)/(hi[0]-lo[0]), (H-2*margin)/(hi[1]-lo[1]))
    off = np.array([(W-s*(hi[0]-lo[0]))/2, (H-s*(hi[1]-lo[1]))/2])
    img = np.ones((H, W, 3)); zb = np.full((H, W), -np.inf)
    L = np.array(light) / np.linalg.norm(light)
    for T, rgb in meshes:
        P = T @ M.T
        n = np.cross(P[:, 1]-P[:, 0], P[:, 2]-P[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
        shade = 0.35 + 0.65*np.abs(n @ L)
        xy = (P[:, :, :2] - lo[:2]) * s + off; xy[:, :, 1] = H - xy[:, :, 1]
        z = P[:, :, 2]
        for k in range(len(T)):
            (x0, y0), (x1, y1), (x2, y2) = xy[k]
            xmin, xmax = int(max(min(x0, x1, x2), 0)), int(min(max(x0, x1, x2), W-1)) + 1
            ymin, ymax = int(max(min(y0, y1, y2), 0)), int(min(max(y0, y1, y2), H-1)) + 1
            if xmax <= xmin or ymax <= ymin: continue
            den = (y1-y2)*(x0-x2) + (x2-x1)*(y0-y2)
            if abs(den) < 1e-9: continue
            gx, gy = np.meshgrid(np.arange(xmin, xmax)+0.5, np.arange(ymin, ymax)+0.5)
            w0 = ((y1-y2)*(gx-x2) + (x2-x1)*(gy-y2)) / den
            w1 = ((y2-y0)*(gx-x2) + (x0-x2)*(gy-y2)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any(): continue
            zz = w0*z[k, 0] + w1*z[k, 1] + w2*z[k, 2]
            sub = zb[ymin:ymax, xmin:xmax]
            m &= zz > sub
            sub[m] = zz[m]
            img[ymin:ymax, xmin:xmax][m] = np.array(rgb) * shade[k]
    # dark outline where depth jumps
    d = np.where(np.isfinite(zb), zb, lo[2]-10)
    edge = (np.abs(np.diff(d, axis=0, prepend=d[:1])) > 0.6) | (np.abs(np.diff(d, axis=1, prepend=d[:, :1])) > 0.6)
    img[edge] *= 0.35
    return img
