<?php

namespace App\Enums;

enum UserQualificationTypeEnum : string
{
    case ELEMENTARY          = 'elementary_education';
    case HIGHSCHOOL          = 'high_school';
    case EXTRACOURSE         = 'extracurricular_course';
    case TECHNICAL_COURSE    = 'technical_course';
    case GRADUATE_DEGREE     = 'undergraduate_degree';
    case POSTGRADUATE_DEGREE = 'postgraduate_degree';
    case MASTER_DEGREE       = 'master_degree';
    case DOCTORATE_DEGREE    = 'doctorate_degree';
}
