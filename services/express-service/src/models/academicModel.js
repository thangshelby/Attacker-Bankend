import mongoose from 'mongoose';
import mongooseUniqueValidator from 'mongoose-unique-validator';

const AcademicSchema = mongoose.Schema({
  student_id: { type: String, ref: 'Student', required: true },
  current_gpa: { type: Number, required: true },
  total_credits_earned: { type: Number, required: true },
  failed_course_count: { type: Number, required: true },
  achievement_award_count: { type: Number, required: true },
  has_scholarship: { type: Boolean, default: false },
  scholarship_count: { type: Number },
  extracurricular_activities_count: { type: Number },
  has_leadership_role: { type: Boolean },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

AcademicSchema.plugin(mongooseUniqueValidator, {
  message: 'already exists.',
});
const AcademicModel = mongoose.model('Academic', AcademicSchema);

export default AcademicModel;
