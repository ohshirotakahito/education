from dataclasses import dataclass


@dataclass(frozen=True)
class ShirtSize:
    name: str
    garment_chest: float
    garment_shoulder: float
    garment_length: float


SIZES = [
    ShirtSize("S", 100, 44, 66),
    ShirtSize("M", 106, 47, 69),
    ShirtSize("L", 112, 50, 72),
    ShirtSize("XL", 120, 54, 75),
    ShirtSize("XXL", 128, 58, 78),
]

FIT_EASE = {
    "すっきり": 8,
    "標準": 12,
    "ゆったり": 18,
    "オーバーサイズ": 24,
}


def recommend_size(height, chest, shoulder, fit):
    """身体寸法と好みから、規格表の中で最も近いサイズを返す。"""
    if fit not in FIT_EASE:
        raise ValueError("着用感を正しく選択してください。")
    if not 130 <= height <= 220:
        raise ValueError("身長は130〜220 cmで入力してください。")
    if not 60 <= chest <= 160:
        raise ValueError("胸囲は60〜160 cmで入力してください。")
    if not 30 <= shoulder <= 75:
        raise ValueError("肩幅は30〜75 cmで入力してください。")

    target_chest = chest + FIT_EASE[fit]
    ideal_length = 0.42 * height
    scored = []
    for size in SIZES:
        chest_gap = size.garment_chest - chest
        too_tight_penalty = max(0, 6 - chest_gap) * 8
        score = (
            abs(size.garment_chest - target_chest) * 2.2
            + abs(size.garment_shoulder - shoulder) * 1.4
            + abs(size.garment_length - ideal_length) * 0.7
            + too_tight_penalty
        )
        scored.append({
            "size": size.name,
            "score": round(score, 1),
            "chest_gap": round(chest_gap, 1),
            "garment_chest": size.garment_chest,
            "garment_shoulder": size.garment_shoulder,
            "garment_length": size.garment_length,
        })
    scored.sort(key=lambda item: item["score"])
    return scored


def fit_description(chest_gap):
    if chest_gap < 6:
        return "かなりタイト"
    if chest_gap < 10:
        return "すっきり"
    if chest_gap < 16:
        return "標準"
    if chest_gap < 23:
        return "ゆったり"
    return "かなりゆったり"
