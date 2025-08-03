import mongoose from 'mongoose';
import mongooseUniqueValidator from 'mongoose-unique-validator';

const AcademicSchema = mongoose.Schema({
  student_id: { type: String, required: true },
  gpa: { type: Number, required: true },
  current_gpa: { type: Number, required: true },
  total_credits_earned: { type: Number, required: true },
  failed_course_count: { type: Number, required: true },
  achievement_award_count: { type: Number, required: true },
  has_scholarship: { type: Boolean, default: false },
  scholarship_count: { type: Number },
  club: { type: String },
  extracurricular_activity_count: { type: Number },
  has_leadership_role: { type: Boolean },
  study_year: { type: String, required: true },
  term: { type: Number, required: true },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

AcademicSchema.plugin(mongooseUniqueValidator, {
  message: 'already exists.',
});
const AcademicModel = mongoose.model('Academic', AcademicSchema);

export default AcademicModel;
