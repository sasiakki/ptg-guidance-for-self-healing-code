import {
  Student,
  Student_training
} from '../models';
import { Student_training_calmtools_rule } from './student-training-calmtools.rule';
import { Student_training_cbp_rule } from './student-training-cbp.rule';
import { Student_training_ceopen_rule } from './student-training-ceopen.rule';
import { Student_training_ahcas_rule } from './student-training-ahcas.rule';
import { Student_training_12hrce_rule } from './student-training-12hrce.rule';
import { Student_training_os_rule } from './student-training-os.rule';
import { Student_training_bt_rule } from './student-training-bt.rule';
import { Student_training_ebt_rule } from './student-training-ebt.rule';
import { Student_training_refresher_rule } from './student-training-refresher.rule';
import { Constants } from './consts';
import * as _ from 'lodash';

export class Student_training_rules {
  constructor() { }

  public static isEligible(
    student: Student,
    trainings: Student_training[],
    course_code: string
  ): string {
    switch (course_code) {
      // case Constants.training_code.CE_OPEN_LIB.CODE:
      //   return Student_training_ceopen_rule.isOpenCEEligible(student,trainings);
      case Constants.training_code.CE_12.CODE:
        return Student_training_12hrce_rule.is12hrCEEligible(student,trainings);
      // case Constants.training_code.CBP_WINTER2019.CODE:
      //   return Student_training_cbp_rule.isCBPEligible(student, trainings);
      // case Constants.training_code.MINDFUL_WC.CODE:
      //   return Student_training_calmtools_rule.isCalmToolsEligible(student,trainings);
      case Constants.training_code.OS.CODE:
        return Student_training_os_rule.isOsEligible(student, trainings);
      case Constants.training_code.BT_7.CODE:
      case Constants.training_code.BT_9.CODE:
      case Constants.training_code.BT_30.CODE:
      case Constants.training_code.BT_70.CODE:
        return Student_training_bt_rule.isBtEligible(student, trainings, course_code);
      // case Constants.training_code.EXEMPT_BT70.CODE:
      //   return Student_training_ebt_rule.isEbtEligible(student, trainings);
      case Constants.training_code.REFRESHER.CODE:
        return Student_training_refresher_rule.isRefresherEligible(student, trainings);
      case Constants.training_code.AHCAS.CODE:
        return Student_training_ahcas_rule.isAhcasEligible(student);
      default:
        return Constants.eligible_training_status.CLOSE; 
    }
  }

}
