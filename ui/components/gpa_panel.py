import customtkinter as ctk

_gpa_cache: dict = {}   # (semester_ids_tuple) -> (term_gpa, cumulative_gpa)

class GPAPanel:
    def __init__(self, parent, current_semester, all_semesters, font_course):
        self.frame = None
        self._build(parent, current_semester, all_semesters, font_course)

    def destroy(self):
        if self.frame is not None:
            self.frame.destroy()

    def _build(self, parent, semester, all_semesters, font_course):
        from services.scale_service import get_all_scales, get_scale_for_course
        from services.course_service import get_courses_for_semester
        from services.calculator import get_semester_gpa, get_cumulative_gpa

        self.frame = ctk.CTkFrame(master=parent, corner_radius=20, width=300)
        self.frame.pack(pady=10, fill="x", padx=10)

        # Load a grading scale with boundaries for GPA calculation
        all_scales = get_all_scales()
        scale = get_scale_for_course(all_scales[0].id) if all_scales else None

        if semester is None:
            ctk.CTkLabel(
                master=self.frame, text="No semester selected.",
                font=font_course
            ).pack(pady=15)
            return

        # ── GPA Calculations (cached) ─────────────────────────────────────────
        cache_key = (semester.id, tuple(s.id for s in all_semesters))
        if cache_key in _gpa_cache:
            term_gpa, cumulative_gpa = _gpa_cache[cache_key]
        else:
            term_courses = get_courses_for_semester(semester.id, load_categories=True)
            term_gpa = get_semester_gpa(term_courses, scale) if scale else None

            course_term_pairs = []
            for sem in all_semesters:
                sem_courses = get_courses_for_semester(sem.id, load_categories=True)
                for course in sem_courses:
                    course_term_pairs.append((course, sem.term))

            cumulative_gpa = get_cumulative_gpa(course_term_pairs, scale) if scale else None
            _gpa_cache[cache_key] = (term_gpa, cumulative_gpa)

        # ── Term GPA ──────────────────────────────────────────────────────────
        if term_gpa is not None:
            ctk.CTkLabel(
                master=self.frame,
                text=f"Term GPA: {round(term_gpa, 2)}",
                font=font_course
            ).pack(pady=(15, 5))
        else:
            ctk.CTkLabel(
                master=self.frame,
                text="Term GPA: N/A",
                font=font_course
            ).pack(pady=(15, 5))

        # ── Cumulative GPA ────────────────────────────────────────────────────
        if cumulative_gpa is not None:
            ctk.CTkLabel(
                master=self.frame,
                text=f"Cumulative GPA: {round(cumulative_gpa, 2)}",
                font=font_course
            ).pack(pady=(0, 15))
        else:
            ctk.CTkLabel(
                master=self.frame,
                text="Cumulative GPA: N/A",
                font=font_course
            ).pack(pady=(0, 15))