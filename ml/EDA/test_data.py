from typing import Tuple


def generate_predict_data(annual_inc: float, dti: float, revol_util: float, emp_length_num: int,
                          grade: str, purpose: str, term: str) -> Tuple[int, int, int, int, int, int, int]:
    # Assuming you have individual variables

    # Grade label
    grade_label = 1 if grade in ['C', 'D', 'E', 'F', 'G'] else 0
    # Purpose label
    purpose_label = 1 if purpose in ['small_business', 'other', 'moving', 'vacation', 'major_purchase', 'medical',
                                     'wedding', 'debt_consolidation'] else 0
    # Term label
    term_label = 1 if term in [' 60 months'] else 0
    # Emp length num label
    emp_length_num_label = 1 if emp_length_num in [0, 1, 2, 10] else 0
    # Annual income label
    annual_inc_lte_60000 = 1 if annual_inc <= 60000 else 0
    # Short emp label
    # short_emp_eq_1 = 1 if short_emp == 1 else 0
    # DTI label
    dti_gte_18 = 1 if dti >= 18 else 0
    # Revol util label
    revol_util_gt_60 = 1 if revol_util > 60 else 0
    return annual_inc_lte_60000, dti_gte_18, revol_util_gt_60, emp_length_num_label, grade_label, purpose_label, term_label
