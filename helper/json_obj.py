from typing import Optional, Dict, Any
from pandas import DataFrame


def json_obj(response: Optional[Dict], extra: str = "") -> DataFrame:
    try:
        code: str = response.get("code")
        if code in {0}:
            data = response.get("data")
            if extra != "":
                data = data.get(extra)
            if isinstance(data, Dict):
                return DataFrame.from_dict(data, orient="index").transpose()
            else:
                return DataFrame(data)
        else:
            raise ValueError(response.get("msg"))
    except Exception as e:
        print(f"Cann't get data: {e}")
    return DataFrame([])

def json_obj_success(response: Optional[Dict]) -> DataFrame:
    try:
        code: str = response.get("code")
        if code in {"000000"}:
            return response.get("success")
        else:
            raise ValueError(response.get("msg"))
    except Exception as e:
        print(f"Cann't get success: {e}")
    return False
