import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                <span className="font-tamil text-primary-600">வொகாப்</span>
                <span className="text-secondary-600">Tamil</span>
              </h1>
            </div>
            <div className="flex space-x-4">
              <Link href="/login" className="btn-outline">
                Login
              </Link>
              <Link href="/register" className="btn-primary">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Master Tamil Vocabulary
            <span className="block text-primary-600 font-tamil">தமிழ் கற்றுக்கொள்ளுங்கள்</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Learn Tamil words through gamified quizzes, adaptive learning, and spaced repetition. 
            Track your progress and compete with friends!
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link href="/register" className="btn-primary text-lg px-8 py-3">
              Start Learning Free
            </Link>
            <Link href="/demo" className="btn-outline text-lg px-8 py-3">
              Try Demo
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="card text-center">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Adaptive Learning</h3>
            <p className="text-gray-600">
              Our smart algorithm adjusts difficulty based on your performance and learning pace.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-4">🔥</div>
            <h3 className="text-xl font-semibold mb-2">Daily Streaks</h3>
            <p className="text-gray-600">
              Build consistent learning habits with daily goals and streak tracking.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-4">🏆</div>
            <h3 className="text-xl font-semibold mb-2">Gamification</h3>
            <p className="text-gray-600">
              Earn XP, unlock achievements, and compete on leaderboards.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-4">🔊</div>
            <h3 className="text-xl font-semibold mb-2">Audio Pronunciation</h3>
            <p className="text-gray-600">
              Learn correct pronunciation with native speaker audio recordings.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">Progress Tracking</h3>
            <p className="text-gray-600">
              Monitor your learning journey with detailed analytics and insights.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-4">🎮</div>
            <h3 className="text-xl font-semibold mb-2">Interactive Quizzes</h3>
            <p className="text-gray-600">
              Multiple quiz formats: MCQ, fill-in-blanks, audio recognition, and more.
            </p>
          </div>
        </div>

        {/* Sample Words Preview */}
        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Sample Tamil Words
          </h2>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {[
              { tamil: 'அன்பு', transliteration: 'anbu', meaning: 'love' },
              { tamil: 'நன்றி', transliteration: 'nandri', meaning: 'thanks' },
              { tamil: 'வணக்கம்', transliteration: 'vanakkam', meaning: 'hello' },
              { tamil: 'மகிழ்ச்சி', transliteration: 'magizhchi', meaning: 'happiness' },
            ].map((word, index) => (
              <div key={index} className="card-hover">
                <div className="tamil-word text-primary-600 mb-2">
                  {word.tamil}
                </div>
                <div className="text-sm text-gray-500 mb-1">
                  {word.transliteration}
                </div>
                <div className="text-gray-700 font-medium">
                  {word.meaning}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl p-8 text-white">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Start Your Tamil Journey?
          </h2>
          <p className="text-xl mb-6 opacity-90">
            Join thousands of learners mastering Tamil vocabulary
          </p>
          <Link href="/register" className="bg-white text-primary-600 hover:bg-gray-100 font-bold py-3 px-8 rounded-lg transition-colors duration-200">
            Create Free Account
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2024 VocabTamil. Built with ❤️ for Tamil learners.</p>
        </div>
      </footer>
    </div>
  );
}
