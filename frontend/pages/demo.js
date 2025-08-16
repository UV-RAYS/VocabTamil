import React, { useState } from 'react';
import Head from 'next/head';

export default function Demo() {
  const [selectedQuizOption, setSelectedQuizOption] = useState(null);
  const [showQuizResult, setShowQuizResult] = useState(false);

  const handleQuizSelect = (optionIndex) => {
    setSelectedQuizOption(optionIndex);
    setTimeout(() => {
      setShowQuizResult(true);
    }, 500);
  };

  const sampleWords = [
    { tamil: 'வணக்கம்', meaning: 'Hello', learned: true },
    { tamil: 'நன்றி', meaning: 'Thank you', learned: true },
    { tamil: 'புத்தகம்', meaning: 'Book', learned: false },
    { tamil: 'பள்ளி', meaning: 'School', learned: false },
  ];

  const achievements = [
    { icon: '🔥', title: 'First Steps', description: 'Complete your first lesson', unlocked: true },
    { icon: '⚡', title: 'Speed Learner', description: 'Answer 10 questions in under 30 seconds', unlocked: true },
    { icon: '🎯', title: 'Perfect Score', description: 'Get 100% on a quiz', unlocked: false },
    { icon: '📚', title: 'Bookworm', description: 'Learn 100 new words', unlocked: false },
  ];

  const leaderboard = [
    { name: 'Priya', score: 2450, rank: 1 },
    { name: 'Arjun', score: 2380, rank: 2 },
    { name: 'Meera', score: 2250, rank: 3 },
    { name: 'You', score: 1890, rank: 4 },
  ];

  return (
    <>
      <Head>
        <title>VocabTamil - Vibrant Design Demo</title>
        <meta name="description" content="Experience the beautiful, vibrant design of VocabTamil" />
      </Head>

      {/* Floating Background Shapes */}
      <div className="floating-shapes">
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
      </div>

      {/* Navigation */}
      <nav className="navbar">
        <div className="container-custom">
          <div className="flex items-center justify-between py-4">
            <div className="navbar-brand">
              VocabTamil
            </div>
            <div className="navbar-nav">
              <div className="nav-item active">
                <span className="nav-link cursor-pointer">Home</span>
              </div>
              <div className="nav-item">
                <span className="nav-link cursor-pointer">Learn</span>
              </div>
              <div className="nav-item">
                <span className="nav-link cursor-pointer">Quiz</span>
              </div>
              <div className="nav-item">
                <span className="nav-link cursor-pointer">Progress</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section section-padding">
        <div className="container-custom text-center">
          <h1 className="hero-title">
            Master Tamil with Style! 🎨
          </h1>
          <p className="hero-subtitle">
            Experience our beautifully redesigned learning platform with vibrant colors, smooth animations, and engaging interactions.
          </p>
          <div className="hero-cta">
            <button className="btn btn-primary btn-lg">
              Start Learning
            </button>
            <button className="btn btn-outline btn-lg">
              View Demo
            </button>
          </div>
        </div>
      </section>

      <div className="container-custom section-padding">
        {/* Stats Dashboard */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Your Progress Dashboard</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">127</div>
              <div className="stat-label">Words Learned</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">15</div>
              <div className="stat-label">Day Streak</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">89%</div>
              <div className="stat-label">Quiz Accuracy</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">2,450</div>
              <div className="stat-label">Total XP</div>
            </div>
          </div>
        </section>

        {/* Word Cards */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Today's Words</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {sampleWords.map((word, index) => (
              <div key={index} className={`word-card ${word.learned ? 'word-card-learned' : ''}`}>
                <div className="text-center">
                  <div className="tamil-word-display">
                    {word.tamil}
                  </div>
                  <div className="word-meaning mb-4">
                    {word.meaning}
                  </div>
                  <div className="flex items-center justify-center space-x-4">
                    <button className="audio-button">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L4.617 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.617l3.766-3.793a1 1 0 01.617-.207zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.983 5.983 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.984 3.984 0 00-1.172-2.828 1 1 0 010-1.415z" clipRule="evenodd" />
                      </svg>
                    </button>
                    {word.learned && (
                      <span className="badge badge-success">Learned</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Quiz Interface */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Interactive Quiz</h2>
          <div className="quiz-container">
            <div className="quiz-progress">
              <div className="quiz-progress-fill" style={{ width: '60%' }}></div>
            </div>
            <div className="quiz-question">
              What does "புத்தகம்" mean in English?
            </div>
            <div className="quiz-options">
              {['Book', 'School', 'Teacher', 'Student'].map((option, index) => (
                <div
                  key={index}
                  className={`quiz-option ${
                    selectedQuizOption === index ? 'selected' : ''
                  } ${
                    showQuizResult && index === 0 ? 'correct' : 
                    showQuizResult && selectedQuizOption === index && index !== 0 ? 'incorrect' : ''
                  }`}
                  onClick={() => !showQuizResult && handleQuizSelect(index)}
                >
                  <div className="text-lg font-medium">{option}</div>
                </div>
              ))}
            </div>
            <div className="text-center">
              <button className="btn btn-primary" disabled={selectedQuizOption === null}>
                {showQuizResult ? 'Next Question' : 'Submit Answer'}
              </button>
            </div>
          </div>
        </section>

        {/* Streak Display */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Learning Streak</h2>
          <div className="max-w-md mx-auto">
            <div className="streak-display">
              <div className="streak-flame">🔥</div>
              <div className="streak-number">15</div>
              <div className="text-xl font-semibold text-gray-700">Days in a row!</div>
              <div className="text-gray-600 mt-2">Keep it up! You're on fire!</div>
            </div>
          </div>
        </section>

        {/* Achievements */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Achievements</h2>
          <div className="achievement-grid">
            {achievements.map((achievement, index) => (
              <div key={index} className={`achievement-card ${achievement.unlocked ? 'unlocked' : 'locked'}`}>
                <div className="achievement-icon">
                  {achievement.icon}
                </div>
                <h3 className="text-xl font-semibold text-center mb-2">
                  {achievement.title}
                </h3>
                <p className="text-gray-600 text-center text-sm">
                  {achievement.description}
                </p>
                {achievement.unlocked && (
                  <div className="text-center mt-3">
                    <span className="badge badge-success">Unlocked!</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Leaderboard */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Leaderboard</h2>
          <div className="max-w-2xl mx-auto">
            {leaderboard.map((user, index) => (
              <div key={index} className="leaderboard-item">
                <div className={`leaderboard-rank rank-${user.rank <= 3 ? user.rank : 'other'}`}>
                  {user.rank}
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-lg">{user.name}</div>
                  <div className="text-gray-600">{user.score.toLocaleString()} XP</div>
                </div>
                {user.rank === 1 && <div className="text-2xl">👑</div>}
                {user.rank === 2 && <div className="text-2xl">🥈</div>}
                {user.rank === 3 && <div className="text-2xl">🥉</div>}
              </div>
            ))}
          </div>
        </section>

        {/* Loading States Demo */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Loading States</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="loading-card"></div>
            <div className="card p-6">
              <div className="loading-text mb-4"></div>
              <div className="loading-text mb-4" style={{ width: '80%' }}></div>
              <div className="loading-text" style={{ width: '60%' }}></div>
            </div>
            <div className="card p-6">
              <div className="flex items-center space-x-4">
                <div className="loading-spinner"></div>
                <div className="text-gray-600">Loading your progress...</div>
              </div>
            </div>
          </div>
        </section>

        {/* Button Showcase */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Button Styles</h2>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="btn btn-primary">Primary</button>
            <button className="btn btn-secondary">Secondary</button>
            <button className="btn btn-accent">Accent</button>
            <button className="btn btn-success">Success</button>
            <button className="btn btn-warning">Warning</button>
            <button className="btn btn-error">Error</button>
            <button className="btn btn-outline">Outline</button>
            <button className="btn btn-ghost">Ghost</button>
          </div>
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            <button className="btn btn-primary btn-sm">Small</button>
            <button className="btn btn-secondary">Regular</button>
            <button className="btn btn-accent btn-lg">Large</button>
          </div>
        </section>

        {/* Typography Showcase */}
        <section className="mb-16">
          <h2 className="heading-2 text-center mb-8">Typography</h2>
          <div className="text-center space-y-4">
            <h1 className="heading-1">Heading 1 - Gradient Text</h1>
            <h2 className="heading-2">Heading 2 - Bold and Clear</h2>
            <h3 className="heading-3">Heading 3 - Semibold</h3>
            <h4 className="heading-4">Heading 4 - Medium Weight</h4>
            <div className="tamil-word-large">தமிழ்</div>
            <div className="tamil-meaning">Beautiful Tamil Typography</div>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              This is regular paragraph text with proper spacing and readability. 
              The design system ensures consistent typography across all components.
            </p>
            <div className="text-gradient text-2xl font-bold">Gradient Text Effect</div>
            <div className="text-gradient-accent text-2xl font-bold">Accent Gradient</div>
          </div>
        </section>
      </div>

      {/* Floating Action Button */}
      <button className="fab">
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </>
  );
}
