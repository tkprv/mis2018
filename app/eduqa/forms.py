# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory, QuerySelectField
from app.main import db
from models import *
from app.staff.models import (StaffAcademicPositionRecord,
                              StaffAcademicPosition,
                              StaffEduDegree)

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class ProgramForm(ModelForm):
    class Meta:
        model = EduQAProgram


class AcademicPositionRecordForm(ModelForm):
    class Meta:
        model = StaffAcademicPositionRecord
    position = QuerySelectField(u'ตำแหน่ง',
                                get_label='fullname_th',
                                query_factory=lambda: StaffAcademicPosition.query.all())


class EduDegreeRecordForm(ModelForm):
    class Meta:
        model = StaffEduDegree


class EduProgramForm(ModelForm):
    class Meta:
        model = EduQAProgram


class EduCurriculumnForm(ModelForm):
    class Meta:
        model = EduQACurriculum
    program = QuerySelectField(u'โปรแกรม',
                                   get_label='name',
                                   query_factory=lambda: EduQAProgram.query.all())


class EduCurriculumnRevisionForm(ModelForm):
    class Meta:
        model = EduQACurriculumnRevision
    curriculum = QuerySelectField(u'หลักสูตร',
                                   get_label='th_name',
                                   query_factory=lambda: EduQACurriculum.query.all()
                                   )


class EduCourseCategoryForm(ModelForm):
    class Meta:
        model = EduQACourseCategory


class EduCourseForm(ModelForm):
    class Meta:
        model = EduQACourse
    category = QuerySelectField(u'หมวด',
                                  get_label='category',
                                  query_factory=lambda: EduQACourseCategory.query.all()
                                  )