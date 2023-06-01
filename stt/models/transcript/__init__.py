from pydantic import confloat, constr

ProbabilityType = confloat(ge=0.0, le=1.0)
LanguageType = constr(regex=r"^(fr|en)$")
