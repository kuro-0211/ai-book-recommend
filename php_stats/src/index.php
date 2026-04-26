<?php
header('Content-Type: text/html; charset=UTF-8');
mb_internal_encoding('UTF-8');
date_default_timezone_set('Asia/Seoul');
require_once __DIR__ . '/db.php';

$error = null;
$rows = [];
$totalAll = 0;
$weeklyTop = [];

try {
    $pdo = get_pdo();

    // 키워드별 추천 횟수 (created_at 은 DB에 UTC로 저장되어 있으므로 KST로 변환)
    $sql = "SELECT keyword,
                   COUNT(*) AS hit_count,
                   DATE_FORMAT(
                     CONVERT_TZ(MAX(created_at), '+00:00', '+09:00'),
                     '%Y-%m-%d %H:%i:%s'
                   ) AS last_used
            FROM recommender_recommendation
            GROUP BY keyword
            ORDER BY hit_count DESC, last_used DESC
            LIMIT 100";
    $rows = $pdo->query($sql)->fetchAll();

    $totalAll = (int)$pdo->query(
        "SELECT COUNT(*) FROM recommender_recommendation"
    )->fetchColumn();

    // n8n이 채우는 최근 주간 TOP5 (가장 최신 week_start 기준)
    $latestWeek = $pdo->query(
        "SELECT MAX(week_start) FROM recommender_weeklytopkeyword"
    )->fetchColumn();
    if ($latestWeek) {
        $stmt = $pdo->prepare(
            "SELECT rank_no, keyword, hit_count
             FROM recommender_weeklytopkeyword
             WHERE week_start = :w
             ORDER BY rank_no ASC"
        );
        $stmt->execute([':w' => $latestWeek]);
        $weeklyTop = $stmt->fetchAll();
    }
} catch (Throwable $e) {
    $error = $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>📊 추천 통계</title>
  <style>
    body { font-family: -apple-system, "Segoe UI", "Noto Sans KR", sans-serif;
           max-width: 800px; margin: 40px auto; padding: 0 20px; color: #222; background: #fafafa; }
    h1 { margin-bottom: 4px; }
    .subtitle { color: #666; margin-top: 0; }
    table { border-collapse: collapse; width: 100%; background: #fff; border-radius: 8px; overflow: hidden; }
    th, td { padding: 10px 12px; border-bottom: 1px solid #eee; text-align: left; }
    th { background: #2b6cb0; color: #fff; font-weight: 600; }
    tr:last-child td { border-bottom: none; }
    .num { text-align: right; font-variant-numeric: tabular-nums; }
    .empty { color: #888; padding: 20px; background: #fff; border-radius: 8px; }
    .error { background: #fff5f5; color: #c53030; padding: 12px 14px; border-radius: 8px; }
    h2 { margin-top: 32px; }
    .pill { display: inline-block; background: #2b6cb0; color: #fff; padding: 2px 10px;
            border-radius: 999px; font-size: 13px; margin-left: 8px; }
    a { color: #2b6cb0; }
  </style>
</head>
<body>
  <h1>📊 추천 통계 <span class="pill">PHP / LAMP</span></h1>
  <p class="subtitle">
    Django 앱: <a href="http://localhost:8000/">http://localhost:8000/</a>
    &nbsp;|&nbsp; 누적 추천 요청: <strong><?= number_format($totalAll) ?></strong>건
  </p>

  <?php if ($error): ?>
    <div class="error">DB 오류: <?= htmlspecialchars($error) ?></div>
  <?php endif; ?>

  <h2>주간 TOP 5 키워드 <small style="color:#888;">(n8n이 매주 월 09:00에 갱신)</small></h2>
  <?php if (!empty($weeklyTop)): ?>
    <table>
      <thead>
        <tr><th style="width:60px;">순위</th><th>키워드</th><th class="num" style="width:120px;">검색 횟수</th></tr>
      </thead>
      <tbody>
      <?php foreach ($weeklyTop as $r): ?>
        <tr>
          <td>#<?= (int)$r['rank_no'] ?></td>
          <td><?= htmlspecialchars($r['keyword']) ?></td>
          <td class="num"><?= number_format((int)$r['hit_count']) ?></td>
        </tr>
      <?php endforeach; ?>
      </tbody>
    </table>
  <?php else: ?>
    <div class="empty">아직 집계된 주간 TOP 데이터가 없습니다. n8n 워크플로가 실행되면 표시됩니다.</div>
  <?php endif; ?>

  <h2>키워드별 추천 횟수 (전체)</h2>
  <?php if (!empty($rows)): ?>
    <table>
      <thead>
        <tr><th>키워드</th><th class="num" style="width:120px;">횟수</th><th style="width:200px;">마지막 요청</th></tr>
      </thead>
      <tbody>
      <?php foreach ($rows as $r): ?>
        <tr>
          <td><?= htmlspecialchars($r['keyword']) ?></td>
          <td class="num"><?= number_format((int)$r['hit_count']) ?></td>
          <td><?= htmlspecialchars($r['last_used']) ?></td>
        </tr>
      <?php endforeach; ?>
      </tbody>
    </table>
  <?php else: ?>
    <div class="empty">아직 추천 기록이 없습니다. <a href="http://localhost:8000/">메인 페이지</a>에서 키워드를 입력해 보세요.</div>
  <?php endif; ?>
</body>
</html>
