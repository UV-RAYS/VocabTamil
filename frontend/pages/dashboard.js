import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useQuery } from 'react-query';
import { progressAPI, wordsAPI, quizAPI } from '../lib/api';
import Link from 'next/link';

export default function Dashboard() {
  const { user, logout } = useAuth();
  
  const { data: dashboardData, isLoading } = useQuery(
    'dashboard',
    progressAPI.getDashboard,
    { enabled: !!user }
  );

  const { data: dailyWords } = useQuery(
    'dailyWords',
    () => wordsAPI.getDailyWords(5),
    { enabled: !!user }
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                <span className="font-tamil text-primary-600">வொகாப்</span>
                <span className="text-secondary-600">Tamil</span>
              </h1>
            </div>
            
            <nav className="hidden md:flex space-x-8">
              <Link href="/dashboard" className="text-primary-600 font-medium">
                Dashboard
              </Link>
              <Link href="/learn" className="text-gray-500 hover:text-gray-700">
                Learn
              </Link>
              <Link href="/quiz" className="text-gray-500 hover:text-gray-700">
                Quiz
              </Link>
              <Link href="/progress" className="text-gray-500 hover:text-gray-700">
                Progress
              </Link>
              <Link href="/leaderboard" className="text-gray-500 hover:text-gray-700">
                Leaderboard
              </Link>
            </nav>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {user?.total_xp || 0} XP
              </div>
              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            வணக்கம், {user?.first_name || user?.username}! 👋
          </h1>
          <p className="text-gray-600">
            Ready to continue your Tamil learning journey?
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-2">
              {user?.current_streak || 0}
            </div>
            <div className="text-sm text-gray-600">Day Streak</div>
            <div className="text-2xl mt-1">🔥</div>
          </div>

          <div className="card text-center">
            <div className="text-3xl font-bold text-secondary-600 mb-2">
              {user?.total_xp || 0}
            </div>
            <div className="text-sm text-gray-600">Total XP</div>
            <div className="text-2xl mt-1">⭐</div>
          </div>

          <div className="card text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {user?.words_learned_count || 0}
            </div>
            <div className="text-sm text-gray-600">Words Learned</div>
            <div className="text-2xl mt-1">📚</div>
          </div>

          <div className="card text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {Math.round(user?.average_accuracy || 0)}%
            </div>
            <div className="text-sm text-gray-600">Accuracy</div>
            <div className="text-2xl mt-1">🎯</div>
          </div>
        </div>

        {/* Daily Progress */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Today's Progress</h2>
            
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span>Daily Goal</span>
                <span>3/{user?.daily_word_goal || 10} words</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${(3 / (user?.daily_word_goal || 10)) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <div className="text-2xl font-bold text-primary-600">240 XP</div>
                <div className="text-sm text-gray-600">Earned today</div>
              </div>
              <Link href="/learn">
                <a className="btn-primary">Continue Learning</a>
              </Link>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            
            <div className="space-y-3">
              <Link href="/learn">
                <a className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">📖</div>
                    <div>
                      <div className="font-medium">Learn New Words</div>
                      <div className="text-sm text-gray-600">Discover today's vocabulary</div>
                    </div>
                  </div>
                </a>
              </Link>

              <Link href="/quiz">
                <a className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">🧠</div>
                    <div>
                      <div className="font-medium">Take a Quiz</div>
                      <div className="text-sm text-gray-600">Test your knowledge</div>
                    </div>
                  </div>
                </a>
              </Link>

              <Link href="/review">
                <a className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3">🔄</div>
                    <div>
                      <div className="font-medium">Review Words</div>
                      <div className="text-sm text-gray-600">Practice previous words</div>
                    </div>
                  </div>
                </a>
              </Link>
            </div>
          </div>
        </div>

        {/* Today's Words Preview */}
        {dailyWords?.words && (
          <div className="card mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Today's Words</h2>
              <Link href="/learn">
                <a className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                  View All →
                </a>
              </Link>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {dailyWords.words.slice(0, 3).map((word) => (
                <div key={word.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="tamil-word text-primary-600 mb-2">
                    {word.tamil_word}
                  </div>
                  <div className="text-sm text-gray-500 mb-1">
                    {word.transliteration}
                  </div>
                  <div className="text-gray-700 font-medium">
                    {word.meanings[0]}
                  </div>
                  {word.audio_url && (
                    <button className="mt-2 text-primary-600 hover:text-primary-700">
                      🔊 Play
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Achievements */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Recent Achievements</h2>
          
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🏆</div>
            <p>Complete your first quiz to earn achievements!</p>
            <Link href="/quiz">
              <a className="btn-primary mt-4 inline-block">Start Quiz</a>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
