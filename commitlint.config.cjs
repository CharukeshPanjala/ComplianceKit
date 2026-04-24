module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'gateway',
        'policy',
        'docs',
        'dsar',
        'common',
        'frontend',
        'infra',
        'ci',
        'deps',
        'release',
        'db'
      ],
    ],
    'subject-case': [
      2,
      'never',
      ['start-case', 'pascal-case', 'upper-case'],
    ],
  },
}