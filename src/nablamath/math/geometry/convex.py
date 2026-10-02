"""Fecho convexo planar exato pelo algoritmo monotone chain."""
from .euclidean import Point2,orientation,polygon_twice_signed_area

def convex_hull(points:tuple[Point2,...])->tuple[Point2,...]:
    ordered=sorted(set(points),key=lambda point:(point.x,point.y))
    if len(ordered)<=1:return tuple(ordered)
    def half(sequence):
        result=[]
        for point in sequence:
            while len(result)>=2 and orientation(result[-2],result[-1],point)<=0: result.pop()
            result.append(point)
        return result
    lower=half(ordered); upper=half(reversed(ordered))
    return tuple(lower[:-1]+upper[:-1])

def is_strictly_convex(polygon:tuple[Point2,...])->bool:
    if len(polygon)<3:return False
    turns=[orientation(polygon[i-2],polygon[i-1],polygon[i]) for i in range(len(polygon))]
    return all(turn>0 for turn in turns) or all(turn<0 for turn in turns)

def contains_convex(polygon:tuple[Point2,...],point:Point2)->bool:
    if len(polygon)<3 or polygon_twice_signed_area(polygon)==0: raise ValueError("polígono degenerado")
    turns=[orientation(polygon[i],polygon[(i+1)%len(polygon)],point) for i in range(len(polygon))]
    return all(turn>=0 for turn in turns) or all(turn<=0 for turn in turns)

__all__=["contains_convex","convex_hull","is_strictly_convex"]
