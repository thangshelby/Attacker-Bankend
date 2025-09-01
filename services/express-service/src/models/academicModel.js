import mongoose from 'mongoose';
import mongooseUniqueValidator from 'mongoose-unique-validator';

const TranscriptSchema = mongoose.Schema({
  file_url: { type: String, required: true },
  file_name: { type: String, required: true },
  file_type: { type: String, enum: ['image', 'pdf'], required: true },
  uploaded_at: { type: Date, default: Date.now },
  processed: { type: Boolean, default: false },
  ocr_data: {
    gpa: { type: Number },
    credits: { type: Number },
    subjects: [{ 
      name: String,
      credit: Number,
      score: Number,
      grade: String
    }],
    semester: { type: String },
    academic_year: { type: String }
  }
});

const AcademicSchema = mongoose.Schema({
  student_id: { type: String, required: true, unique: true },
  gpa: { type: Number, required: true, min: 0, max: 10 },
  current_gpa: { type: Number, required: true, min: 0, max: 10 },
  total_credits_earned: { type: Number, required: true, min: 0 },
  failed_course_count: { type: Number, required: true, min: 0 },
  achievement_award_count: { type: Number, required: true, min: 0 },
  has_scholarship: { type: Boolean, default: false },
  scholarship_count: { type: Number, min: 0 },
  club: { type: String },
  extracurricular_activity_count: { type: Number, min: 0 },
  has_leadership_role: { type: Boolean, default: false },
  study_year: { type: String, required: true },
  term: { type: Number, required: true },
  transcripts: [TranscriptSchema],
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

// Update timestamp before saving
AcademicSchema.pre('save', function(next) {
  this.updated_at = new Date();
  next();
});

AcademicSchema.pre('findOneAndUpdate', function(next) {
  this.set({ updated_at: new Date() });
  next();
});

AcademicSchema.plugin(mongooseUniqueValidator, {
  message: 'already exists.',
});

const AcademicModel = mongoose.model('Academic', AcademicSchema);

export default AcademicModel;
